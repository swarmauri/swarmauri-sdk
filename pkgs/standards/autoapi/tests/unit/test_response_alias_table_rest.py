from __future__ import annotations
import pytest
from autoapi.v3.types import App
from fastapi.testclient import TestClient

from .response_utils import build_alias_model


@pytest.mark.parametrize(
    "alias,check",
    [
        ("json", lambda r: r.json() == {"kind": "json"}),
        ("html", lambda r: r.text == "<h1>html</h1>"),
        ("text", lambda r: r.text == "text"),
        ("file", lambda r: r.content == b"file"),
        ("stream", lambda r: r.content == b"stream"),
        (
            "redirect",
            lambda r: r.status_code in (302, 307)
            and r.headers["location"] == "/target",
        ),
    ],
)
def test_response_alias_table_rest(alias, check, tmp_path):
    Widget = build_alias_model(tmp_path)
    app = App()
    app.include_router(Widget.rest.router)
    client = TestClient(app)
    kwargs = {"json": {}}
    if alias == "redirect":
        kwargs["allow_redirects"] = False
    r = client.post(f"/widget/{alias}", **kwargs)
    assert check(r)
