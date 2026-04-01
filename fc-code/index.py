import base64
import json
from datetime import datetime
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


def route_level_test_start(request: JsonDict) -> Tuple[int, JsonDict]:
    level = request.get("query", {}).get("level")
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        sql = """
            SELECT id, question_type, stem, options_json, level, difficulty
            FROM question_content
            WHERE module_type = 'level_test'
              AND publish_status = 'published'
        """
        params: JsonDict = {}
        if level:
            sql += " AND level = :level"
            params["level"] = level
        sql += " ORDER BY id ASC LIMIT 10"
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()

        questions = []
        for row in rows:
            options = row["options_json"]
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except json.JSONDecodeError:
                    options = []
            questions.append(
                {
                    "id": row["id"],
                    "question_type": row["question_type"],
                    "prompt": row["stem"],
                    "options": options or [],
                    "level_tag": row["level"],
                    "difficulty": row["difficulty"],
                }
            )
        return 200, success({"questions": questions, "count": len(questions)})
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_level_test_submit(request: JsonDict) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    username = payload.get("username")
    answers = payload.get("answers") or []
    if not username:
        raise HttpError(400, "username is required")
    if not isinstance(answers, list) or not answers:
        raise HttpError(400, "answers are required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            user = conn.execute(
                text("SELECT id FROM users WHERE username = :username LIMIT 1"),
                {"username": username},
            ).mappings().first()
            if not user:
                raise HttpError(404, "user not found")

            test_record = conn.execute(
                text(
                    """
                    INSERT INTO level_test_record (user_id, status)
                    VALUES (:user_id, 'submitted')
                    RETURNING id, started_at
                    """
                ),
                {"user_id": user["id"]},
            ).mappings().one()

            correct_count = 0
            total = 0
            level_scores = {"BEC Preliminary": 0, "BEC Vantage": 0, "BEC Higher": 0}
            for item in answers:
                question_id = item.get("question_id")
                user_answer = item.get("user_answer")
                if not question_id:
                    continue
                question = conn.execute(
                    text(
                        """
                        SELECT id, correct_answer, level
                        FROM question_content
                        WHERE id = :question_id AND module_type = 'level_test'
                        LIMIT 1
                        """
                    ),
                    {"question_id": question_id},
                ).mappings().first()
                if not question:
                    continue
                is_correct = str(user_answer).strip() == str(question["correct_answer"]).strip()
                score = 10 if is_correct else 0
                total += score
                if is_correct:
                    correct_count += 1
                    if question["level"] in level_scores:
                        level_scores[question["level"]] += 1
                conn.execute(
                    text(
                        """
                        INSERT INTO level_test_answer (test_record_id, question_id, user_answer, is_correct, score)
                        VALUES (:test_record_id, :question_id, :user_answer, :is_correct, :score)
                        """
                    ),
                    {
                        "test_record_id": test_record["id"],
                        "question_id": question_id,
                        "user_answer": user_answer,
                        "is_correct": is_correct,
                        "score": score,
                    },
                )

            if total >= 80:
                result_level = "BEC Higher"
            elif total >= 50:
                result_level = "BEC Vantage"
            else:
                result_level = "BEC Preliminary"

            ability_summary = (
                f"You answered {correct_count} question(s) correctly. "
                f"Recommended level: {result_level}. "
                f"Level strengths: Preliminary={level_scores['BEC Preliminary']}, "
                f"Vantage={level_scores['BEC Vantage']}, Higher={level_scores['BEC Higher']}."
            )

            conn.execute(
                text(
                    """
                    UPDATE level_test_record
                    SET total_score = :total_score,
                        result_level = :result_level,
                        ability_summary = :ability_summary,
                        ended_at = CURRENT_TIMESTAMP,
                        status = 'completed'
                    WHERE id = :record_id
                    """
                ),
                {
                    "total_score": total,
                    "result_level": result_level,
                    "ability_summary": ability_summary,
                    "record_id": test_record["id"],
                },
            )

        return 200, success(
            {
                "record_id": test_record["id"],
                "total_score": total,
                "result_level": result_level,
                "ability_summary": ability_summary,
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_level_test_result(request: JsonDict, record_id: int) -> Tuple[int, JsonDict]:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            record = conn.execute(
                text(
                    """
                    SELECT ltr.id, ltr.total_score, ltr.result_level, ltr.ability_summary, ltr.status,
                           ltr.started_at, ltr.ended_at, u.username
                    FROM level_test_record ltr
                    JOIN users u ON u.id = ltr.user_id
                    WHERE ltr.id = :record_id
                    LIMIT 1
                    """
                ),
                {"record_id": record_id},
            ).mappings().first()
            if not record:
                raise HttpError(404, "level test record not found")

            answers = conn.execute(
                text(
                    """
                    SELECT lta.question_id, lta.user_answer, lta.is_correct, lta.score, qc.stem, qc.correct_answer
                    FROM level_test_answer lta
                    JOIN question_content qc ON qc.id = lta.question_id
                    WHERE lta.test_record_id = :record_id
                    ORDER BY lta.id ASC
                    """
                ),
                {"record_id": record_id},
            ).mappings().all()

        return 200, success(
            {
                "record": {
                    "id": record["id"],
                    "username": record["username"],
                    "total_score": float(record["total_score"] or 0),
                    "result_level": record["result_level"],
                    "ability_summary": record["ability_summary"],
                    "status": record["status"],
                    "started_at": str(record["started_at"]),
                    "ended_at": str(record["ended_at"]) if record["ended_at"] else None,
                },
                "answers": [
                    {
                        **dict(row),
                        "score": float(row["score"] or 0),
                    }
                    for row in answers
                ],
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_mock_exams_list(request: JsonDict) -> Tuple[int, JsonDict]:
    level = request.get("query", {}).get("level")
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        sql = """
            SELECT id, stem, level, difficulty, question_type
            FROM question_content
            WHERE module_type = 'mock_exam'
              AND publish_status = 'published'
        """
        params: JsonDict = {}
        if level:
            sql += " AND level = :level"
            params["level"] = level
        sql += " ORDER BY id ASC LIMIT 20"
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return 200, success({"items": [dict(row) for row in rows], "count": len(rows)})
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_mock_exam_submit(request: JsonDict, exam_id: int) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    username = payload.get("username")
    answers = payload.get("answers") or []
    if not username:
        raise HttpError(400, "username is required")
    if not isinstance(answers, list) or not answers:
        raise HttpError(400, "answers are required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            user = conn.execute(
                text("SELECT id FROM users WHERE username = :username LIMIT 1"),
                {"username": username},
            ).mappings().first()
            if not user:
                raise HttpError(404, "user not found")

            question_ids = [item.get("question_id") for item in answers if item.get("question_id")]
            if exam_id not in question_ids:
                question_ids.insert(0, exam_id)

            placeholders = ", ".join([f":q{i}" for i in range(len(question_ids))])
            params = {f"q{i}": qid for i, qid in enumerate(question_ids)}
            questions = conn.execute(
                text(
                    f"""
                    SELECT id, correct_answer, level, difficulty
                    FROM question_content
                    WHERE module_type = 'mock_exam' AND id IN ({placeholders})
                    """
                ),
                params,
            ).mappings().all()
            question_map = {row["id"]: row for row in questions}
            if exam_id not in question_map:
                raise HttpError(404, "mock exam question not found")

            exam_record = conn.execute(
                text(
                    """
                    INSERT INTO mock_exam_record (user_id, status)
                    VALUES (:user_id, 'submitted')
                    RETURNING id
                    """
                ),
                {"user_id": user["id"]},
            ).mappings().one()

            correct_count = 0
            processed = 0
            weak_tags = []
            for item in answers:
                question_id = item.get("question_id")
                user_answer = item.get("user_answer")
                question = question_map.get(question_id)
                if not question:
                    continue
                is_correct = str(user_answer).strip() == str(question["correct_answer"]).strip()
                score = 10 if is_correct else 0
                processed += 1
                if is_correct:
                    correct_count += 1
                else:
                    weak_tags.append(f"{question['level']}/{question['difficulty']}")
                conn.execute(
                    text(
                        """
                        INSERT INTO mock_exam_answer (exam_record_id, question_id, user_answer, is_correct, score, explanation_result)
                        VALUES (:exam_record_id, :question_id, :user_answer, :is_correct, :score, :explanation_result)
                        """
                    ),
                    {
                        "exam_record_id": exam_record["id"],
                        "question_id": question_id,
                        "user_answer": user_answer,
                        "is_correct": is_correct,
                        "score": score,
                        "explanation_result": "correct" if is_correct else "needs review",
                    },
                )

            total_score = correct_count * 10
            accuracy_rate = round((correct_count / processed) * 100, 2) if processed else 0
            weak_tags_text = ", ".join(weak_tags) if weak_tags else "none"
            conn.execute(
                text(
                    """
                    UPDATE mock_exam_record
                    SET total_score = :total_score,
                        accuracy_rate = :accuracy_rate,
                        weak_tags = :weak_tags,
                        ended_at = CURRENT_TIMESTAMP,
                        status = 'completed'
                    WHERE id = :record_id
                    """
                ),
                {
                    "total_score": total_score,
                    "accuracy_rate": accuracy_rate,
                    "weak_tags": weak_tags_text,
                    "record_id": exam_record["id"],
                },
            )

        return 200, success(
            {
                "record_id": exam_record["id"],
                "total_score": total_score,
                "accuracy_rate": accuracy_rate,
                "weak_tags": weak_tags_text,
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_mock_exam_result(request: JsonDict, record_id: int) -> Tuple[int, JsonDict]:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            record = conn.execute(
                text(
                    """
                    SELECT mer.id, mer.total_score, mer.accuracy_rate, mer.weak_tags, mer.status,
                           mer.started_at, mer.ended_at, u.username
                    FROM mock_exam_record mer
                    JOIN users u ON u.id = mer.user_id
                    WHERE mer.id = :record_id
                    LIMIT 1
                    """
                ),
                {"record_id": record_id},
            ).mappings().first()
            if not record:
                raise HttpError(404, "mock exam record not found")

            answers = conn.execute(
                text(
                    """
                    SELECT mea.question_id, mea.user_answer, mea.is_correct, mea.score, mea.explanation_result,
                           qc.stem, qc.correct_answer
                    FROM mock_exam_answer mea
                    JOIN question_content qc ON qc.id = mea.question_id
                    WHERE mea.exam_record_id = :record_id
                    ORDER BY mea.id ASC
                    """
                ),
                {"record_id": record_id},
            ).mappings().all()

        return 200, success(
            {
                "record": {
                    "id": record["id"],
                    "username": record["username"],
                    "total_score": float(record["total_score"] or 0),
                    "accuracy_rate": float(record["accuracy_rate"] or 0),
                    "weak_tags": record["weak_tags"],
                    "status": record["status"],
                    "started_at": str(record["started_at"]),
                    "ended_at": str(record["ended_at"]) if record["ended_at"] else None,
                },
                "answers": [
                    {
                        **dict(row),
                        "score": float(row["score"] or 0),
                    }
                    for row in answers
                ],
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_vocab_list(request: JsonDict) -> Tuple[int, JsonDict]:
    level = request.get("query", {}).get("level")
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        sql = """
            SELECT id, word, phonetic, meaning_zh, business_example, collocation, level, difficulty
            FROM vocab_content
            WHERE publish_status = 'published'
        """
        params: JsonDict = {}
        if level:
            sql += " AND level = :level"
            params["level"] = level
        sql += " ORDER BY id ASC LIMIT 20"
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return 200, success({"items": [dict(row) for row in rows], "count": len(rows)})
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_patterns_list(request: JsonDict) -> Tuple[int, JsonDict]:
    level = request.get("query", {}).get("level")
    scene = request.get("query", {}).get("scene")
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        sql = """
            SELECT id, pattern_text, scene_type, function_type, example_text, slot_desc, level, difficulty
            FROM pattern_content
            WHERE publish_status = 'published'
        """
        params: JsonDict = {}
        if level:
            sql += " AND level = :level"
            params["level"] = level
        if scene:
            sql += " AND scene_type = :scene"
            params["scene"] = scene
        sql += " ORDER BY id ASC LIMIT 20"
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return 200, success({"items": [dict(row) for row in rows], "count": len(rows)})
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_scenes_list(request: JsonDict) -> Tuple[int, JsonDict]:
    level = request.get("query", {}).get("level")
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        sql = """
            SELECT id, scene_name, scene_background, training_goal, user_role, ai_role, level, difficulty
            FROM scene_content
            WHERE publish_status = 'published'
        """
        params: JsonDict = {}
        if level:
            sql += " AND level = :level"
            params["level"] = level
        sql += " ORDER BY id ASC LIMIT 20"
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return 200, success({"items": [dict(row) for row in rows], "count": len(rows)})
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_scene_detail(request: JsonDict, scene_id: int) -> Tuple[int, JsonDict]:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, scene_name, scene_background, training_goal, user_role, ai_role,
                           prompt_template, recommended_expression, level, difficulty
                    FROM scene_content
                    WHERE id = :scene_id AND publish_status = 'published'
                    LIMIT 1
                    """
                ),
                {"scene_id": scene_id},
            ).mappings().first()
        if not row:
            raise HttpError(404, "scene not found")
        return 200, success(dict(row))
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_scene_start(request: JsonDict, scene_id: int) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    username = payload.get("username")
    if not username:
        raise HttpError(400, "username is required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            user = conn.execute(
                text("SELECT id, username FROM users WHERE username = :username LIMIT 1"),
                {"username": username},
            ).mappings().first()
            if not user:
                raise HttpError(404, "user not found")

            scene = conn.execute(
                text(
                    """
                    SELECT id, scene_name, training_goal, ai_role, prompt_template, recommended_expression
                    FROM scene_content
                    WHERE id = :scene_id AND publish_status = 'published'
                    LIMIT 1
                    """
                ),
                {"scene_id": scene_id},
            ).mappings().first()
            if not scene:
                raise HttpError(404, "scene not found")

            session = conn.execute(
                text(
                    """
                    INSERT INTO user_scene_session (user_id, scene_id, session_status, round_count)
                    VALUES (:user_id, :scene_id, 'started', 0)
                    RETURNING id, session_status, round_count, started_at
                    """
                ),
                {"user_id": user["id"], "scene_id": scene_id},
            ).mappings().one()

        return 200, success(
            {
                "session_id": session["id"],
                "session_status": session["session_status"],
                "round_count": session["round_count"],
                "started_at": str(session["started_at"]),
                "scene": dict(scene),
                "opening_message": f"Hello {username}, let's begin the scene: {scene['scene_name']}. {scene['training_goal']}",
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_scene_message(request: JsonDict, scene_id: int) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    session_id = payload.get("session_id")
    message = payload.get("message")
    if not session_id or not message:
        raise HttpError(400, "session_id and message are required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            session = conn.execute(
                text(
                    """
                    SELECT uss.id, uss.user_id, uss.scene_id, uss.session_status, uss.round_count,
                           sc.scene_name, sc.training_goal, sc.ai_role, sc.recommended_expression
                    FROM user_scene_session uss
                    JOIN scene_content sc ON sc.id = uss.scene_id
                    WHERE uss.id = :session_id AND uss.scene_id = :scene_id
                    LIMIT 1
                    """
                ),
                {"session_id": session_id, "scene_id": scene_id},
            ).mappings().first()
            if not session:
                raise HttpError(404, "scene session not found")
            if session["session_status"] != "started":
                raise HttpError(400, "scene session is not active")

            new_round_count = int(session["round_count"]) + 1
            ai_reply = (
                f"As the {session['ai_role']}, I understand your point: '{message}'. "
                f"For this scene ({session['scene_name']}), please keep focusing on: {session['training_goal']}"
            )
            feedback = (
                "Good attempt. Try to use one of these business expressions: "
                f"{session['recommended_expression']}"
            )
            user_summary = f"[{datetime.utcnow().isoformat()}] user: {message}"
            ai_summary = f"[{datetime.utcnow().isoformat()}] ai: {ai_reply} | feedback: {feedback}"

            conn.execute(
                text(
                    """
                    UPDATE user_scene_session
                    SET round_count = :round_count,
                        user_summary = COALESCE(user_summary, '') || CASE WHEN COALESCE(user_summary, '') = '' THEN '' ELSE E'\n' END || :user_summary,
                        ai_feedback_summary = COALESCE(ai_feedback_summary, '') || CASE WHEN COALESCE(ai_feedback_summary, '') = '' THEN '' ELSE E'\n' END || :ai_summary
                    WHERE id = :session_id
                    """
                ),
                {
                    "round_count": new_round_count,
                    "user_summary": user_summary,
                    "ai_summary": ai_summary,
                    "session_id": session_id,
                },
            )

        return 200, success(
            {
                "session_id": int(session_id),
                "scene_id": scene_id,
                "round_count": new_round_count,
                "reply": ai_reply,
                "feedback": feedback,
            }
        )
    except HttpError:
        raise
    except SQLAlchemyError as exc:
        raise HttpError(500, "database connection failed", {"error": str(exc)})


def route_scene_finish(request: JsonDict, scene_id: int) -> Tuple[int, JsonDict]:
    payload = request.get("json") or {}
    session_id = payload.get("session_id")
    if not session_id:
        raise HttpError(400, "session_id is required")

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.begin() as conn:
            session = conn.execute(
                text(
                    """
                    SELECT uss.id, uss.session_status, uss.round_count, uss.user_summary, uss.ai_feedback_summary,
                           sc.scene_name, sc.training_goal
                    FROM user_scene_session uss
                    JOIN scene_content sc ON sc.id = uss.scene_id
                    WHERE uss.id = :session_id AND uss.scene_id = :scene_id
                    LIMIT 1
                    """
                ),
                {"session_id": session_id, "scene_id": scene_id},
            ).mappings().first()
            if not session:
                raise HttpError(404, "scene session not found")

            score = min(100, 60 + int(session["round_count"]) * 10)
            summary = (
                f"Scene '{session['scene_name']}' finished. "
                f"You completed {session['round_count']} round(s) and practiced: {session['training_goal']}"
            )
            feedback_summary = (
                f"Keep improving clarity, politeness, and business structure. Suggested score: {score}."
            )

            conn.execute(
                text(
                    """
                    UPDATE user_scene_session
                    SET session_status = 'finished',
                        ended_at = CURRENT_TIMESTAMP,
                        score = :score,
                        user_summary = COALESCE(user_summary, :summary),
                        ai_feedback_summary = COALESCE(ai_feedback_summary, '') || CASE WHEN COALESCE(ai_feedback_summary, '') = '' THEN '' ELSE E'\n' END || :feedback_summary
                    WHERE id = :session_id
                    """
                ),
                {
                    "score": score,
                    "summary": summary,
                    "feedback_summary": feedback_summary,
                    "session_id": session_id,
                },
            )

        return 200, success(
            {
                "session_id": int(session_id),
                "scene_id": scene_id,
                "session_status": "finished",
                "score": score,
                "summary": summary,
                "feedback_summary": feedback_summary,
            }
        )
    except HttpError:
        raise
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
    ("GET", "/api/v1/level-test/start"): route_level_test_start,
    ("POST", "/api/v1/level-test/submit"): route_level_test_submit,
    ("GET", "/api/v1/mock-exams"): route_mock_exams_list,
    ("GET", "/api/v1/vocab"): route_vocab_list,
    ("GET", "/api/v1/patterns"): route_patterns_list,
    ("GET", "/api/v1/scenes"): route_scenes_list,
}


def dispatch(request: JsonDict) -> Tuple[int, JsonDict]:
    route_key = (request["method"], request["path"])
    handler = ROUTES.get(route_key)
    if handler:
        return handler(request)

    path = request["path"]
    method = request["method"]
    if path.startswith("/api/v1/scenes/"):
        suffix = path[len("/api/v1/scenes/"):]
        if suffix.endswith("/start"):
            scene_id_text = suffix[:-len("/start")]
            if scene_id_text.isdigit() and method == "POST":
                return route_scene_start(request, int(scene_id_text))
        elif suffix.endswith("/message"):
            scene_id_text = suffix[:-len("/message")]
            if scene_id_text.isdigit() and method == "POST":
                return route_scene_message(request, int(scene_id_text))
        elif suffix.endswith("/finish"):
            scene_id_text = suffix[:-len("/finish")]
            if scene_id_text.isdigit() and method == "POST":
                return route_scene_finish(request, int(scene_id_text))
        elif suffix.isdigit() and method == "GET":
            return route_scene_detail(request, int(suffix))

    if path.startswith("/api/v1/level-test/result/") and method == "GET":
        record_id_text = path[len("/api/v1/level-test/result/"):]
        if record_id_text.isdigit():
            return route_level_test_result(request, int(record_id_text))

    if path.startswith("/api/v1/mock-exams/"):
        suffix = path[len("/api/v1/mock-exams/"):]
        if suffix.endswith("/submit"):
            exam_id_text = suffix[:-len("/submit")]
            if exam_id_text.isdigit() and method == "POST":
                return route_mock_exam_submit(request, int(exam_id_text))
        if suffix.startswith("result/") and method == "GET":
            record_id_text = suffix[len("result/"):]
            if record_id_text.isdigit():
                return route_mock_exam_result(request, int(record_id_text))

    raise HttpError(
        404,
        "route not found",
        {
            "method": request["method"],
            "path": request["path"],
            "available_routes": [f"{method} {path}" for method, path in ROUTES.keys()],
        },
    )


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
