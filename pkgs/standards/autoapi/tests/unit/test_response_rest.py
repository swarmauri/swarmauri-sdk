from __future__ import annotations
from autoapi.v3.types import App
from fastapi.testclient import TestClient

from .response_utils import build_ping_model


def test_response_rest_call():
    Widget = build_ping_model()
    app = App()
    app.include_router(Widget.rest.router)
    client = TestClient(app)
    r = client.post("/widget/ping", json={})
    assert r.status_code == 200
    assert r.json() == {"pong": True}
