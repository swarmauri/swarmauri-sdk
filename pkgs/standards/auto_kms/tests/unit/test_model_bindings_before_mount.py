import types
import sys

import pytest


@pytest.mark.asyncio
async def test_bindings_before_mount(monkeypatch):
    sys.modules["autoapi.v3.v2"] = types.ModuleType("autoapi.v3.v2")
    jsonrpc_mod = types.ModuleType("autoapi.v3.v2.jsonrpc_models")

    async def _http_exc_to_rpc(*args, **kwargs):
        pass

    jsonrpc_mod._http_exc_to_rpc = _http_exc_to_rpc
    sys.modules["autoapi.v3.v2.jsonrpc_models"] = jsonrpc_mod

    from autoapi.v3.autoapi import AutoAPI
    from autoapi.v3.bindings import rest as rest_binding

    monkeypatch.setattr(
        rest_binding,
        "build_router_and_attach",
        lambda model, specs, only_keys=None: None,
    )

    from autoapi.v3.runtime import executor as _executor

    called: dict[str, object] = {}

    async def fake_invoke(*, request, db, phases, ctx=None):
        called["phases"] = phases
        return "ok"

    monkeypatch.setattr(_executor, "_invoke", fake_invoke)

    from auto_kms.tables.key import Key

    api = AutoAPI()
    api.bind(Key)

    result = await Key.rpc.create(
        {"name": "n", "algorithm": "AES256_GCM", "status": "enabled"}, db=object()
    )

    assert result == "ok"
    assert "HANDLER" in called["phases"]
