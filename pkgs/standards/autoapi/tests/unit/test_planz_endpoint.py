import pytest
from types import SimpleNamespace

from autoapi.v3.system.diagnostics import _build_planz_endpoint
from autoapi.v3.opspec import OpSpec
from autoapi.v3.runtime import plan as _plan


def handler(ctx):
    return None


@pytest.mark.asyncio
async def test_planz_endpoint_sequence(monkeypatch: pytest.MonkeyPatch):
    class API:
        pass

    class Model:
        __name__ = "Model"

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

    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    def fake_flattened_order(plan, *, persist, include_system_steps, deps):
        assert plan is dummy_plan
        if persist:
            return ["sys:txn:begin@START_TX"]
        return []

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)
    data = await planz()

    assert "Model" in data
    assert "write" in data["Model"]
    assert any("sys:txn:begin@START_TX" in s for s in data["Model"]["write"])
    assert "read" in data["Model"]
    assert not any("sys:txn:begin@START_TX" in s for s in data["Model"]["read"])


@pytest.mark.asyncio
async def test_planz_endpoint_emits_atoms_after_plan_compilation():
    class API:
        pass

    class Model:
        __name__ = "Model"

    Model.opspecs = SimpleNamespace(
        all=(
            OpSpec(
                alias="write",
                target="create",
                table=Model,
                persist="default",
                handler=handler,
            ),
        )
    )

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)

    data = await planz()
    steps = data["Model"]["write"]
    assert any(step.startswith("sys:") for step in steps)
    assert not any(step.startswith("atom:") for step in steps)

    from autoapi.v3.runtime import plan as runtime_plan

    runtime_plan.attach_atoms_for_model(Model, {})

    data = await planz()
    steps = data["Model"]["write"]
    assert any(step.startswith("sys:") for step in steps)
    assert any(step.startswith("atom:") for step in steps)
