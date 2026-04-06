#!/usr/bin/env python3
"""Minimal end-to-end script for exercising the FC handler auth + user center APIs."""
from __future__ import annotations

import argparse
import json
import time
from typing import Any, Dict, Iterable, Optional

import httpx


def _print_step(title: str) -> None:
    print(f"\n=== {title} ===")


def _set_auth_token(client: httpx.Client, payload: Dict[str, Any]) -> None:
    data = payload.get("data") or {}
    token = data.get("token")
    if token:
        bearer = f"Bearer {token}"
        client.headers["Authorization"] = bearer
        client.headers["X-BEC-Authorization"] = bearer


def _request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    allowed_status: Optional[Iterable[int]] = None,
    **kwargs,
) -> Dict[str, Any]:
    response = client.request(method, path, **kwargs)
    try:
        payload = response.json()
    except ValueError as exc:  # pragma: no cover - debug helper
        raise SystemExit(f"Non-JSON response from {method} {path}: {exc}\n{response.text}") from exc

    print(f"{method} {path} -> {response.status_code}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if allowed_status and response.status_code in allowed_status:
        return payload
    if response.status_code >= 400:
        raise SystemExit(f"Request failed: {payload}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="BEC Agent auth/user-center smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8081", help="signing-proxy base URL")
    parser.add_argument("--username", help="username to use; auto-generated when omitted")
    parser.add_argument("--email", help="email to use; auto-generated when omitted")
    parser.add_argument("--password", default="TestPass123!", help="initial password")
    parser.add_argument("--new-password", help="password after /password/change")
    parser.add_argument("--reset-password", help="password after /password/reset")
    parser.add_argument("--timeout", type=float, default=30, help="HTTP timeout in seconds")
    args = parser.parse_args()

    username = args.username or f"fc_user_{int(time.time())}"
    email = args.email or f"{username}@example.com"
    initial_password = args.password
    changed_password = args.new_password or f"{initial_password}!1"
    reset_password = args.reset_password or f"{initial_password}!2"

    with httpx.Client(base_url=args.base_url, timeout=args.timeout) as client:
        _print_step("Register user")
        _request(
            client,
            "POST",
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": email,
                "password": initial_password,
            },
            allowed_status={200, 409},
        )

        _print_step("Login with initial password")
        login_payload = _request(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"username": username, "password": initial_password},
        )
        _set_auth_token(client, login_payload)

        _print_step("Update user profile")
        _request(
            client,
            "PUT",
            "/api/v1/users/profile",
            json={
                "username": username,
                "display_name": f"{username} display",
                "avatar_url": "https://placehold.co/96x96",
                "bio": "FC handler smoke test user",
                "phone_number": "+86-10-88888888",
                "company": "BEC Demo Inc.",
                "job_title": "QA Engineer",
                "target_level": "BEC Higher",
                "current_level": "BEC Vantage",
                "learning_goal": "Finish trial curriculum",
            },
        )

        _print_step("Change password")
        _request(
            client,
            "POST",
            "/api/v1/users/password/change",
            json={
                "username": username,
                "current_password": initial_password,
                "new_password": changed_password,
            },
        )

        _print_step("Login with changed password")
        changed_login_payload = _request(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"username": username, "password": changed_password},
        )
        _set_auth_token(client, changed_login_payload)

        _print_step("Request forgot-password token")
        forgot_payload = _request(
            client,
            "POST",
            "/api/v1/users/password/forgot",
            json={"username": username},
        )
        reset_token = forgot_payload["data"].get("reset_token")
        if not reset_token:
            raise SystemExit("reset_token missing in forgot-password response")

        _print_step("Reset password with token")
        _request(
            client,
            "POST",
            "/api/v1/users/password/reset",
            json={"token": reset_token, "new_password": reset_password},
        )

        _print_step("Login with final password")
        final_login_payload = _request(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"username": username, "password": reset_password},
        )
        _set_auth_token(client, final_login_payload)

    print("\nAll auth + user-center API calls completed successfully.")


if __name__ == "__main__":
    main()
