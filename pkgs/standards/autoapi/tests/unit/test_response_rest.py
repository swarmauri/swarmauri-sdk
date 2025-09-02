from __future__ import annotations
import pytest
from autoapi.v3.types import App
from fastapi.testclient import TestClient

from .response_utils import (
    RESPONSE_KINDS,
    build_model_for_response,
    build_ping_model,
)


def test_response_rest_call():
    Widget = build_ping_model()
    app = App()
    app.include_router(Widget.rest.router)
    client = TestClient(app)
    r = client.post("/widget/ping", json={})
    assert r.status_code == 200
    assert r.json() == {"pong": True}


@pytest.mark.parametrize("kind", RESPONSE_KINDS)
def test_response_rest_alias_table(kind, tmp_path):
    Widget, file_path = build_model_for_response(kind, tmp_path)
    app = App()
    app.include_router(Widget.rest.router)
    client = TestClient(app)
    r = client.post("/widget/download", json={})
    if kind == "auto":
        assert r.json() == {"data": {"pong": True}, "ok": True}
    elif kind == "json":
        assert r.json() == {"pong": True}
    elif kind == "html":
        assert r.text == "<h1>pong</h1>"
    elif kind == "text":
        assert r.text == "pong"
    elif kind == "file":
        assert r.content == file_path.read_bytes()
    elif kind == "stream":
        assert r.content == b"pong"
    elif kind == "redirect":
        assert r.status_code == 307
        assert r.headers["location"] == "/redirected"
        return
    assert r.status_code == 200
