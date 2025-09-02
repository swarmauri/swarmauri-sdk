from __future__ import annotations
from types import SimpleNamespace
import pytest

from autoapi.v3.bindings import rpc_call

from .response_utils import build_alias_model


@pytest.mark.parametrize(
    "alias,check",
    [
        ("json", lambda r: r == {"kind": "json"}),
        ("html", lambda r: r == "<h1>html</h1>"),
        ("text", lambda r: r == "text"),
        ("file", lambda r: r.read_text() == "file"),
        ("stream", lambda r: b"".join(r) == b"stream"),
        (
            "redirect",
            lambda r: r.status_code in (302, 307)
            and r.headers["location"] == "/target",
        ),
    ],
)
@pytest.mark.asyncio
async def test_response_alias_table_rpc(alias, check, tmp_path):
    Widget = build_alias_model(tmp_path)
    api = SimpleNamespace(models={"Widget": Widget})
    result = await rpc_call(api, Widget, alias, {}, db=SimpleNamespace())
    assert check(result)
