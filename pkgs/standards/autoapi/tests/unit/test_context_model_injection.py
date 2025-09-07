from types import SimpleNamespace

import pytest

from autoapi.v3.bindings.rest.collection import _ctx
from autoapi.v3.bindings import rpc
from autoapi.v3.op import OpSpec


class DummyModel:
    pass


def test_ctx_includes_model():
    request = SimpleNamespace(state=SimpleNamespace())
    ctx = _ctx(DummyModel, "list", "list", request, db=None, payload={}, parent_kw={})
    assert ctx["model"] is DummyModel


@pytest.mark.asyncio
async def test_rpc_injects_model(monkeypatch):
    called = {}

    async def fake_invoke(*, request, db, phases, ctx):
        called["ctx"] = ctx

    monkeypatch.setattr(rpc, "_executor", SimpleNamespace(_invoke=fake_invoke))
    monkeypatch.setattr(rpc, "_get_phase_chains", lambda model, alias: {})
    monkeypatch.setattr(
        rpc, "_validate_input", lambda model, alias, target, payload: {}
    )

    method = rpc._build_rpc_callable(DummyModel, OpSpec(alias="foo", target="custom"))
    await method({}, db=object())

    assert called["ctx"]["model"] is DummyModel
