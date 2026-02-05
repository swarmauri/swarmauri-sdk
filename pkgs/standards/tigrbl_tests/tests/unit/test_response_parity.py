from __future__ import annotations
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl.bindings import rpc_call
from tigrbl.types import App
from .response_utils import build_ping_model


@pytest.mark.asyncio
async def test_response_rest_rpc_parity():
    Widget = build_ping_model()
    app = App()
    app.include_router(Widget.rest.router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        rest_result = (await client.post("/widget/ping", json={})).json()
    api = SimpleNamespace(models={"Widget": Widget})
    rpc_result = await rpc_call(api, Widget, "ping", {}, db=SimpleNamespace())
    assert rest_result == rpc_result == {"pong": True}
