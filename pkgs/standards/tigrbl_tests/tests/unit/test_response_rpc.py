from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl import TigrblApp
from tigrbl.mapping import include_table

from .response_utils import (
    RESPONSE_KINDS,
    build_model_for_jinja_response,
    build_model_for_response,
    build_model_for_response_non_alias,
    build_ping_model,
)


@pytest.mark.asyncio
async def test_response_rpc_call_attached_to_table_router_and_app():
    Widget = build_ping_model()

    assert callable(getattr(Widget, "rpc_call", None))

    router = SimpleNamespace()
    include_table(router, Widget, mount_router=False)
    assert callable(getattr(router, "rpc_call", None))

    app = TigrblApp()
    app.include_table(Widget)
    assert callable(getattr(app, "rpc_call", None))


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", RESPONSE_KINDS)
async def test_response_rpc_alias_table(kind, tmp_path):
    Widget, _ = build_model_for_response(kind, tmp_path)
    result = await Widget.rpc_call("download", {}, db=SimpleNamespace())
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", RESPONSE_KINDS)
async def test_response_rpc_non_alias_table(kind, tmp_path):
    Widget, _ = build_model_for_response_non_alias(kind, tmp_path)
    result = await Widget.rpc_call("download", {}, db=SimpleNamespace())
    assert result is not None


@pytest.mark.asyncio
async def test_response_rpc_alias_table_jinja(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    result = await Widget.rpc_call("download", {}, db=SimpleNamespace())
    assert result is not None
