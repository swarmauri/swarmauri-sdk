from __future__ import annotations

import json

import pytest

from tigrbl.requests import Request


def _make_request(*, headers: dict[str, str], body: bytes = b"") -> Request:
    return Request(
        method="POST",
        path="/session",
        headers=headers,
        query={},
        path_params={},
        body=body,
        scope={"client": ("203.0.113.10", 443)},
    )


def test_request_headers_and_cookies_support_nested_dot_notation_access() -> None:
    request = _make_request(
        headers={
            "Authorization": "Bearer access-token",
            "Cookie": "sid=session-token; tenant=acme",
        }
    )

    assert request.headers.authorization == "Bearer access-token"
    assert request.headers.cookie.sid == "session-token"
    assert request.headers.cookie.tenant == "acme"


def test_request_cookie_header_supports_many_cookies_with_terse_getters() -> None:
    request = _make_request(
        headers={
            "Cookie": "sid=session-token; tenant=acme; theme=dark; mode=compact",
        }
    )

    assert request.headers.get("cookie", "")
    assert request.headers.cookie.sid == "session-token"
    assert request.headers.cookie.tenant == "acme"
    assert request.headers.cookie.theme == "dark"
    assert request.cookies.get("sid") == "session-token"
    assert request.cookies.get("tenant") == "acme"
    assert request.cookies.get("theme") == "dark"
    assert request.cookies.get("mode") == "compact"


@pytest.mark.asyncio()
async def test_request_exposes_json_and_dot_notation_bearer_conveniences() -> None:
    request = _make_request(
        headers={"Authorization": "Bearer access-token"},
        body=json.dumps({"ok": True}).encode("utf-8"),
    )

    assert request.json() == {"ok": True}
    assert await request.json() == {"ok": True}
    assert request.bearer_token == "access-token"
    assert request.session_token == "access-token"


def test_request_session_token_falls_back_to_cookie_and_client_ip_attribute() -> None:
    request = _make_request(headers={"Cookie": "sid=session-token"})

    assert request.session_token == "session-token"
    assert request.client.ip == "203.0.113.10"


def test_request_exposes_b64url_helpers_via_dot_notation() -> None:
    request = _make_request(headers={})

    token = request.b64url_encode(b'{"alg":"HS256"}')

    assert token == "eyJhbGciOiJIUzI1NiJ9"
    assert request.b64url_decode(token) == b'{"alg":"HS256"}'
