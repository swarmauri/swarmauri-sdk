from __future__ import annotations

import json

import pytest

from tigrbl.requests import Request


def _make_request(path: str, body: bytes | None = None) -> Request:
    return Request(
        method="POST",
        path=path,
        headers={"content-type": "application/json"},
        query={},
        path_params={},
        body=body or b"",
    )


@pytest.mark.asyncio()
async def test_request_supports_request_url_path_and_body_and_async_json() -> None:
    req = _make_request("/users/42", json.dumps({"id": 42}).encode("utf-8"))

    assert req.url.path == "/users/42"
    assert req.body == b'{"id": 42}'
    assert await req.json() == {"id": 42}


def test_request_json_is_usable_without_await_for_blocking_style() -> None:
    req = _make_request("/users", json.dumps({"ok": True, "id": 1}).encode("utf-8"))

    payload = req.json()

    assert payload["ok"] is True
    assert payload.get("id") == 1
    assert dict(payload) == {"ok": True, "id": 1}
