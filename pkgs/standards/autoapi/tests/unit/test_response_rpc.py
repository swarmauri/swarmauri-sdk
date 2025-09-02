from __future__ import annotations
from types import SimpleNamespace
import pytest

from autoapi.v3.bindings import rpc_call

from .response_utils import build_ping_model


@pytest.mark.asyncio
async def test_response_rpc_call():
    Widget = build_ping_model()
    api = SimpleNamespace(models={"Widget": Widget})
    result = await rpc_call(api, Widget, "ping", {}, db=SimpleNamespace())
    assert result == {"pong": True}
