from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl.runtime.executor.invoke import _invoke
from tigrbl.runtime.gw.invoke import invoke as gw_invoke
from tigrbl.runtime.gw.raw import GwRawEnvelope


@pytest.mark.asyncio
async def test_executor_invoke_returns_response_object() -> None:
    async def _handler(ctx):
        ctx.response = SimpleNamespace(result={"ok": True})

    response = await _invoke(
        request=None,
        db=None,
        phases={"HANDLER": [_handler]},
        ctx={"op": "read"},
    )

    assert response is not None
    assert getattr(response, "result", None) == {"ok": True}


@pytest.mark.asyncio
async def test_gateway_invoke_returns_executor_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = object()
    response_obj = SimpleNamespace(result={"ok": True})

    class _Plan:
        ingress_chain = {}
        opmeta = [SimpleNamespace(model=object(), alias="read")]
        phase_chains = {0: {"HANDLER": []}}

    class _Kernel:
        def kernel_plan(self, _app):
            return _Plan()

        def get_opview(self, _app, _model, _alias):
            return object()

    sent = {"called": False, "ctx": None}

    async def _fake_send_transport_response(_env, ctx):
        sent["called"] = True
        sent["ctx"] = ctx

    async def _fake_executor_invoke(*, request, db, phases, ctx):
        return response_obj

    async def _recv() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def _send(_message: dict[str, object]) -> None:
        return None

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "http", "app": app},
        receive=_recv,
        send=_send,
    )

    from importlib import import_module

    mod = import_module("tigrbl.runtime.gw.invoke")

    async def _noop_phase_chain(ctx, phases):
        return None

    monkeypatch.setattr(mod, "Kernel", _Kernel)
    monkeypatch.setattr(mod, "_run_phase_chain", _noop_phase_chain)
    monkeypatch.setattr(mod, "_resolve_op_index", lambda ctx, plan: 0)
    monkeypatch.setattr(mod, "_invoke", _fake_executor_invoke)
    monkeypatch.setattr(mod, "_send_transport_response", _fake_send_transport_response)

    returned = await gw_invoke(env)

    assert returned is response_obj
    assert sent["called"] is True
    assert getattr(getattr(sent["ctx"], "response", None), "result", None) == {"ok": True}
