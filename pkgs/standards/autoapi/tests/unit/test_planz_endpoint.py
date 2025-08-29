import pytest
from types import SimpleNamespace

from autoapi.v3.system import diagnostics as _diag
from autoapi.v3.system.diagnostics import _build_planz_endpoint
from autoapi.v3.opspec import OpSpec
from autoapi.v3.runtime import plan as _plan


class DummyLabel:
    def __init__(self, text: str, anchor: str, kind: str = "atom") -> None:
        self.text = text
        self.anchor = anchor
        self.kind = kind

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.text


def sample_hook(ctx):
    return None


sample_hook.__autoapi_domain__ = "emit"


@pytest.mark.asyncio
async def test_planz_endpoint_sequence(monkeypatch: pytest.MonkeyPatch):
    class API:
        pass

    class Model:
        __name__ = "Model"

    def handler(ctx):
        return None

    Model.opspecs = SimpleNamespace(
        all=(
            OpSpec(
                alias="write",
                target="create",
                table=Model,
                persist="default",
                handler=handler,
            ),
            OpSpec(
                alias="read",
                target="read",
                table=Model,
                persist="skip",
                handler=handler,
            ),
        )
    )

    Model.hooks = SimpleNamespace(write=SimpleNamespace(PRE_HANDLER=[sample_hook]))

    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    def fake_flattened_order(plan, *, persist, include_system_steps, deps):
        assert plan is dummy_plan
        if persist:
            return [
                DummyLabel("secdep:prep", "PREP", kind="secdep"),
                DummyLabel("dep:handler", "HANDLER", kind="dep"),
                DummyLabel("sys:txn:begin@START_TX", "START_TX", kind="sys"),
            ]
        return []

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)
    data = await planz()

    assert "Model" in data
    assert "write" in data["Model"]
    hook_label = "hook:emit:sample_hook@PRE_HANDLER"
    assert hook_label in data["Model"]["write"]
    assert "secdep:prep" in data["Model"]["write"]
    assert "dep:handler" in data["Model"]["write"]
    assert "sys:txn:begin@START_TX" in data["Model"]["write"]
    assert "read" in data["Model"]
    assert not any("sys:txn:begin@START_TX" in s for s in data["Model"]["read"])


@pytest.mark.asyncio
async def test_planz_endpoint_prefers_compiled_plan_for_atoms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When a compiled plan is attached, atoms come from flattened_order."""

    class API:
        pass

    class Model:
        __name__ = "Model"

    def handler(ctx):
        return None

    Model.opspecs = SimpleNamespace(
        all=(
            OpSpec(
                alias="create",
                target="create",
                table=Model,
                persist="default",
                handler=handler,
            ),
        )
    )

    Model.hooks = SimpleNamespace(create=SimpleNamespace(PRE_HANDLER=[sample_hook]))

    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    calls = {"flatten": False, "chains": False}

    def fake_flattened_order(plan, *, persist, include_system_steps, deps):
        calls["flatten"] = True
        return [
            DummyLabel("sys:txn:begin@START_TX", "START_TX", kind="sys"),
            DummyLabel(
                "atom:emit:paired_pre@emit:aliases:pre_flush",
                "emit:aliases:pre_flush",
                kind="atom",
            ),
        ]

    def fake_build_phase_chains(model, alias):
        calls["chains"] = True
        return {}

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)
    monkeypatch.setattr(_diag, "build_phase_chains", fake_build_phase_chains)

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)
    data = await planz()

    assert calls["flatten"] is True
    assert calls["chains"] is False
    hook_label = "hook:emit:sample_hook@PRE_HANDLER"
    assert data["Model"]["create"] == [
        hook_label,
        "sys:txn:begin@START_TX",
        "atom:emit:paired_pre@emit:aliases:pre_flush",
    ]
