import pytest


@pytest.mark.asyncio
async def test_bindings_before_mount(monkeypatch):
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

    from auto_kms.orm import Key

    api = AutoAPI()
    api.bind(Key)

    result = await Key.rpc.create(
        {"name": "n", "algorithm": "AES256_GCM", "status": "enabled"}, db=object()
    )

    assert result == "ok"
    assert "HANDLER" in called["phases"]
