import base64
import json
from hashlib import sha256
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.parse import parse_qs

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from src.core.config import settings


JsonDict = Dict[str, Any]
RouteHandler = Callable[[JsonDict], Tuple[int, JsonDict]]


class HttpError(Exception):
    def __init__(self, status_code: int, message: str, data: Optional[JsonDict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.data = data or {}


def success(data: Optional[JsonDict] = None, message: str = "success") -> JsonDict:
    return {
        "code": 0,
        "message": message,
        "data": data or {},
    }


def error(code: int, message: str, data: Optional[JsonDict] = None) -> JsonDict:
    return {
        "code": code,
        "message": message,
        "data": data or {},
    }


def json_response(status_code: int, payload: JsonDict) -> JsonDict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8"
        },
        "body": json.dumps(payload, ensure_ascii=False),
    }


def normalize_event(event: Any) -> JsonDict:
    if isinstance(event, bytes):
        event = event.decode("utf-8", errors="ignore")
    if isinstance(event, str):
        event = event.strip()
        if not event:
            return {}
        try:
            return json.loads(event)
        except json.JSONDecodeError:
            return {"raw": event}
    if isinstance(event, dict):
        return event
    return {"raw": str(event)}


def parse_request(event_obj: JsonDict) -> JsonDict:
    request_context = event_obj.get("requestContext", {}) or {}
    http_ctx = request_context.get("http", {}) or {}

    method = (
        event_obj.get("httpMethod")
        or event_obj.get("method")
        or http_ctx.get("method")
        or "GET"
    ).upper()

    path = (
        event_obj.get("path")
        or event_obj.get("rawPath")
        or http_ctx.get("path")
        or "/"
    )

    raw_query = event_obj.get("rawQueryString") or ""
    query = event_obj.get("queryParameters") or {}
    if not query and raw_query:
        query = {k: v[0] if isinstance(v, list) and v else "" for k, v in parse_qs(raw_query).items()}

    headers = event_obj.get("headers") or {}
    body = event_obj.get("body")
    if body and event_obj.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8", errors="ignore")

    json_body = None
    if isinstance(body, str) and body.strip():
        try:
            json_body = json.loads(body)
        except json.JSONDecodeError:
            json_body = None

    return {
        "method": method,
        "path": path,
        "query": query,
        "headers": headers,
        "body": body,
        "json": json_body,
        "event": event_obj,
    }


def route_health(request: JsonDict) -> Tuple[int, JsonDict]:
    return 200, success(
        {
            "status": "ok",
            "service": "bec-agent-api",
            "runtime": "python3.10",
            "path": request["path"],
            "mode": "fc-native-handler",
        }
    )


def route_ping(request: JsonDict) -> Tuple[int, JsonDict]:
    return 200, success(
        {
            "service": "bec-agent-api",
            "path": request["path"],
        },
        message="pong",
    )


def _hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def route_auth_login(request: JsonDict) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        raise HttpError(400, "username and password are required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, username, status, password_hash
                    FROM users
                    WHERE username = :username
                    LIMIT 1
                    """
                ),
                {"username": username},
            ).mappings().first()
        if not row or row["password_hash"] != _hash_password(password):
            raise HttpError(401, "invalid username or password")
        return 200, success(
            {
                "id": row["id"],
                "username": row["username"],
                "status": row["status"],
            }
        )
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_auth_register(request: JsonDict) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    username = payload.get("username")
    email = payload.get("email")
    password = payload.get("password")
    if not username or not password:
        raise HttpError(400, "username and password are required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            existing = conn.execute(
                text(
                    """
                    SELECT id FROM users
                    WHERE username = :username
                       OR (:email IS NOT NULL AND email = :email)
                    LIMIT 1
                    """
                ),
                {"username": username, "email": email},
            ).first()
            if existing:
                raise HttpError(409, "username or email already exists")

            user_row = conn.execute(
                text(
                    """
                    INSERT INTO users (username, email, password_hash, status, register_source)
                    VALUES (:username, :email, :password_hash, 'active', 'api')
                    RETURNING id, username, email, status
                    """
                ),
                {
                    "username": username,
                    "email": email,
                    "password_hash": _hash_password(password),
                },
            ).mappings().one()
            conn.execute(
                text(
                    """
                    INSERT INTO user_profile (user_id)
                    VALUES (:user_id)
                    ON CONFLICT (user_id) DO NOTHING
                    """
                ),
                {"user_id": user_row["id"]},
            )
        return 200, success(dict(user_row))
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_users_me(request: JsonDict) -> Tuple[int, JsonDict]:
    username = request.get("query", {}).get("username")
    if not username:
        raise HttpError(400, "username is required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, username, email, status
                    FROM users
                    WHERE username = :username
                    LIMIT 1
                    """
                ),
                {"username": username},
            ).mappings().first()
        if not row:
            raise HttpError(404, "user not found")
        return 200, success(dict(row))
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_users_profile(request: JsonDict) -> Tuple[int, JsonDict]:
    username = request.get("query", {}).get("username")
    if not username:
        raise HttpError(400, "username is required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            user = conn.execute(
                text(
                    """
                    SELECT id, username, email, status
                    FROM users
                    WHERE username = :username
                    LIMIT 1
                    """
                ),
                {"username": username},
            ).mappings().first()
            if not user:
                raise HttpError(404, "user not found")

            if request["method"] == "PUT":
                payload = request.get("json") or {}
                conn.execute(
                    text(
                        """
                        INSERT INTO user_profile (
                            user_id, target_level, current_level, industry_background, learning_goal, learning_preference
                        ) VALUES (
                            :user_id, :target_level, :current_level, :industry_background, :learning_goal, :learning_preference
                        )
                        ON CONFLICT (user_id) DO UPDATE SET
                            target_level = EXCLUDED.target_level,
                            current_level = EXCLUDED.current_level,
                            industry_background = EXCLUDED.industry_background,
                            learning_goal = EXCLUDED.learning_goal,
                            learning_preference = EXCLUDED.learning_preference,
                            updated_at = CURRENT_TIMESTAMP
                        """
                    ),
                    {
                        "user_id": user["id"],
                        "target_level": payload.get("target_level"),
                        "current_level": payload.get("current_level"),
                        "industry_background": payload.get("industry_background"),
                        "learning_goal": payload.get("learning_goal"),
                        "learning_preference": payload.get("learning_preference"),
                    },
                )

            profile = conn.execute(
                text(
                    """
                    SELECT target_level, current_level, industry_background, learning_goal, learning_preference
                    FROM user_profile
                    WHERE user_id = :user_id
                    LIMIT 1
                    """
                ),
                {"user_id": user["id"]},
            ).mappings().first()
        return 200, success(
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "status": user["status"],
                "profile": dict(profile) if profile else None,
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_db_health(request: JsonDict) -> Tuple[int, JsonDict]:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS ok")).scalar()
            db_info = conn.execute(
                text(
                    """
                    SELECT current_database() AS db_name,
                           current_user AS db_user,
                           current_schema() AS schema_name
                    """
                )
            ).mappings().one()
            users_exists = conn.execute(
                text(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'users'
                    )
                    """
                )
            ).scalar()
            users_count = None
            if users_exists:
                users_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        return 200, success(
            {
                "status": "ok",
                "database": "postgresql",
                "check": result,
                "database_name": db_info["db_name"],
                "database_user": db_info["db_user"],
                "schema": db_info["schema_name"],
                "users_table_exists": bool(users_exists),
                "users_count": users_count,
                "host": "8.147.56.124",
            }
        )
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


ROUTES: Dict[Tuple[str, str], RouteHandler] = {
    ("GET", "/api/v1/health"): route_health,
    ("GET", "/health"): route_health,
    ("GET", "/api/v1/ping"): route_ping,
    ("GET", "/ping"): route_ping,
    ("GET", "/api/v1/db/health"): route_db_health,
    ("POST", "/api/v1/auth/login"): route_auth_login,
    ("POST", "/api/v1/auth/register"): route_auth_register,
    ("GET", "/api/v1/users/me"): route_users_me,
    ("GET", "/api/v1/users/profile"): route_users_profile,
    ("PUT", "/api/v1/users/profile"): route_users_profile,
}


def dispatch(request: JsonDict) -> Tuple[int, JsonDict]:
    route_key = (request["method"], request["path"])
    handler = ROUTES.get(route_key)
    if not handler:
        raise HttpError(
            404,
            "route not found",
            {
                "method": request["method"],
                "path": request["path"],
                "available_routes": [f"{method} {path}" for method, path in ROUTES.keys()],
            },
        )
    return handler(request)


def handler(event, context):
    try:
        event_obj = normalize_event(event)
        request = parse_request(event_obj)
        status_code, payload = dispatch(request)
        return json_response(status_code, payload)
    except HttpError as exc:
        return json_response(exc.status_code, error(exc.status_code, exc.message, exc.data))
    except Exception as exc:
        return json_response(
            500,
            error(
                500,
                "internal server error",
                {"error": str(exc)},
            ),
        )
