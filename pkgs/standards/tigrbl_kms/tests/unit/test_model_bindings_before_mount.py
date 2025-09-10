import pytest


@pytest.mark.asyncio
async def test_bindings_before_mount(monkeypatch):
    from tigrbl.v3 import TigrblApp
    from tigrbl.v3.bindings import rest as rest_binding

    monkeypatch.setattr(
        rest_binding,
        "build_router_and_attach",
        lambda model, specs, api=None, only_keys=None: None,
    )

    from tigrbl.v3.runtime import executor as _executor

    called: dict[str, object] = {}

    async def fake_invoke(*, request, db, phases, ctx=None):
        called["phases"] = phases
        return "ok"

    monkeypatch.setattr(_executor, "_invoke", fake_invoke)

    from tigrbl_kms.orm import Key

    api = TigrblApp()
    api.bind(Key)

    result = await Key.rpc.create(
        {"name": "n", "algorithm": "AES256_GCM", "status": "enabled"}, db=object()
    )

    assert result == "ok"
    assert "HANDLER" in called["phases"]
