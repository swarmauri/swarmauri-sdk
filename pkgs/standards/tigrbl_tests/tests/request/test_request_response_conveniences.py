from __future__ import annotations

import json

import pytest

from tigrbl.responses import Response
from tigrbl.requests import Request


def _make_request(
    *,
    path: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> Request:
    return Request(
        method=method,
        path=path,
        headers=headers or {},
        query={},
        path_params={},
        body=body or b"",
        scope={
            "type": "http",
            "method": method,
            "path": path,
            "headers": [
                (name.lower().encode("latin-1"), value.encode("latin-1"))
                for name, value in (headers or {}).items()
            ],
        },
    )


@pytest.mark.asyncio()
async def test_request_supports_async_json_cookie_header_and_url_path() -> None:
    req = _make_request(
        path="/admin/",
        method="POST",
        headers={"Cookie": "session=abc123", "X-Admin-Key": "secret"},
        body=json.dumps({"ok": True}).encode("utf-8"),
    )

    assert await req.json() == {"ok": True}
    assert req.cookies.get("session") == "abc123"
    assert req.headers.get("X-Admin-Key", "") == "secret"
    assert req.url.path.rstrip("/") or "/" == "/admin"


@pytest.mark.asyncio()
async def test_request_json_empty_body_is_none() -> None:
    req = _make_request(path="/")

    assert await req.json() is None


def test_response_supports_text_json_headers_and_cookies() -> None:
    resp = Response.json({"ok": True}, headers={"X-Trace": "abc"})

    assert resp.json_body() == {"ok": True}
    assert resp.body_text == '{"ok":true}'
    assert resp.headers_map.get("x-trace", "") == "abc"

    resp.set_cookie("session", "abc123")
    assert resp.cookies.get("session") == "abc123"
