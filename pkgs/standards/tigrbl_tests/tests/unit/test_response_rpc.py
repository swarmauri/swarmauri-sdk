from __future__ import annotations
from types import SimpleNamespace
import pytest

from tigrbl._concrete import Body
from tigrbl.mapping import rpc_call

from .response_utils import (
    RESPONSE_KINDS,
    build_model_for_jinja_response,
    build_model_for_response,
    build_model_for_response_non_alias,
    build_ping_model,
)


@pytest.mark.asyncio
async def test_response_rpc_call():
    Widget = build_ping_model()
    app = SimpleNamespace(tables={"Widget": Widget})
    result = await rpc_call(app, Widget, "ping", {}, db=SimpleNamespace())
    assert result == {"pong": True}


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", RESPONSE_KINDS)
async def test_response_rpc_alias_table(kind, tmp_path):
    Widget, file_path = build_model_for_response(kind, tmp_path)
    app = SimpleNamespace(tables={"Widget": Widget})
    result = await rpc_call(app, Widget, "download", {}, db=SimpleNamespace())
    if kind == "auto":
        assert Body(result["body"]).json() == {"data": {"pong": True}, "ok": True}
    elif kind == "json":
        assert Body(result["body"]).json() == {"pong": True}
    elif kind == "html":
        assert result["body"] == b"<h1>pong</h1>"
    elif kind == "text":
        assert result["body"] == b"pong"
    elif kind == "file":
        assert result["path"] == str(file_path)
    elif kind == "stream":
        content = b"".join(chunk async for chunk in result["body_iterator"])
        assert content == b"pong"
    elif kind == "redirect":
        assert result["status_code"] == 307
        headers = dict(result["raw_headers"])
        assert headers[b"location"].decode() == "/redirected"
        return
    if kind not in {"auto", "json"}:
        assert result["status_code"] == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", RESPONSE_KINDS)
async def test_response_rpc_non_alias_table(kind, tmp_path):
    Widget, file_path = build_model_for_response_non_alias(kind, tmp_path)
    app = SimpleNamespace(tables={"Widget": Widget})
    result = await rpc_call(app, Widget, "download", {}, db=SimpleNamespace())
    if kind == "auto":
        assert Body(result["body"]).json() == {"data": {"pong": True}, "ok": True}
    elif kind == "json":
        assert Body(result["body"]).json() == {"pong": True}
    elif kind == "html":
        assert result["body"] == b"<h1>pong</h1>"
    elif kind == "text":
        assert result["body"] == b"pong"
    elif kind == "file":
        assert result["path"] == str(file_path)
    elif kind == "stream":
        content = b"".join(chunk async for chunk in result["body_iterator"])
        assert content == b"pong"
    elif kind == "redirect":
        assert result["status_code"] == 307
        headers = dict(result["raw_headers"])
        assert headers[b"location"].decode() == "/redirected"
        return
    if kind not in {"auto", "json"}:
        assert result["status_code"] == 200


@pytest.mark.asyncio
async def test_response_rpc_alias_table_jinja(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    app = SimpleNamespace(tables={"Widget": Widget})
    result = await rpc_call(app, Widget, "download", {}, db=SimpleNamespace())
    assert result["status_code"] == 200
    assert result["body"] == b"<h1>World</h1>"
