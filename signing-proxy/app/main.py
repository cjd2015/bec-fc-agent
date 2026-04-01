from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import httpx
from dotenv import load_dotenv
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient
from Tea.request import TeaRequest

load_dotenv()

app = FastAPI(title="BEC FC Signing Proxy", version="1.2.0")

FC_BASE_URL = os.getenv("FC_BASE_URL", "https://your-fc-url.cn-hangzhou.fcapp.run")
FC_TIMEOUT = int(os.getenv("FC_TIMEOUT", "60"))
ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
ALIYUN_SECURITY_TOKEN = os.getenv("ALIYUN_SECURITY_TOKEN", "")

HOP_BY_HOP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "transfer-encoding",
    "content-encoding",
}


def build_acs3_authorization(method: str, target_url: str, headers: dict) -> str:
    parsed_url = urlparse(target_url)
    auth_request = TeaRequest()
    auth_request.method = method.upper()
    auth_request.pathname = parsed_url.path.replace("$", "%24")
    auth_request.headers = headers
    auth_request.query = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
    return OpenApiUtilClient.get_authorization(
        auth_request,
        "ACS3-HMAC-SHA256",
        "",
        ALIYUN_ACCESS_KEY_ID,
        ALIYUN_ACCESS_KEY_SECRET,
    )


@app.get("/health")
async def health():
    return {
        "code": 0,
        "message": "success",
        "data": {
            "status": "ok",
            "service": "signing-proxy",
            "fc_base_url": FC_BASE_URL,
            "auth_configured": bool(ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET),
        },
    }


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    if not ALIYUN_ACCESS_KEY_ID or not ALIYUN_ACCESS_KEY_SECRET:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "fc function auth credentials not configured",
                "data": None,
            },
        )

    base = FC_BASE_URL.rstrip("/")
    query_string = request.url.query
    target_url = f"{base}/{full_path}"
    if query_string:
        target_url = f"{target_url}?{query_string}"

    body = await request.body()
    upstream_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS and k.lower() != "authorization"
    }

    acs_date = datetime.utcnow().isoformat("T")[:19] + "Z"
    upstream_headers["x-acs-date"] = acs_date
    if ALIYUN_SECURITY_TOKEN:
        upstream_headers["x-acs-security-token"] = ALIYUN_SECURITY_TOKEN

    authorization = build_acs3_authorization(
        method=request.method,
        target_url=target_url,
        headers=upstream_headers,
    )
    upstream_headers["authorization"] = authorization

    async with httpx.AsyncClient(timeout=FC_TIMEOUT) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=upstream_headers,
                content=body,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers={
                    k: v
                    for k, v in resp.headers.items()
                    if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}
                },
            )
        except httpx.HTTPError as e:
            return JSONResponse(
                status_code=502,
                content={
                    "code": 502,
                    "message": "proxy request failed",
                    "data": {"error": str(e)},
                },
            )
