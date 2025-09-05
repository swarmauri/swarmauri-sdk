import pytest
from types import SimpleNamespace

from autoapi.v3.system import diagnostics as _diag
from autoapi.v3.system.diagnostics import _build_planz_endpoint
from autoapi.v3.ops import OpSpec
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


def dep_fn(ctx):
    return None


def secdep_fn(ctx):
    return None


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
                deps=(dep_fn,),
                secdeps=(secdep_fn,),
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

    Model.hooks = SimpleNamespace(
        write=SimpleNamespace(PRE_HANDLER=[sample_hook], HANDLER=[handler])
    )

    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    dep_label = _diag._label_callable(dep_fn)
    secdep_label = _diag._label_callable(secdep_fn)
    handler_hook_label = _diag._label_hook(handler, "HANDLER")

    def fake_flattened_order(
        plan,
        *,
        persist,
        include_system_steps,
        deps,
        secdeps,
        hooks,
    ):
        assert plan is dummy_plan
        if persist:
            hook_label = _diag._label_hook(sample_hook, "PRE_HANDLER")
            assert hooks == {
                "PRE_HANDLER": [hook_label],
                "HANDLER": [handler_hook_label],
            }
            assert set(deps) == {dep_label}
            assert secdeps == [secdep_label]
            return [
                f"PRE_TX:secdep:{secdep_label}",
                f"PRE_TX:dep:{dep_label}",
                "START_TX:hook:sys:txn:begin@START_TX",
                f"PRE_HANDLER:{hook_label}",
                "HANDLER:hook:sys:handler:crud@HANDLER",
                "END_TX:hook:sys:txn:commit@END_TX",
            ]
        return []

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)
    data = await planz()

    assert "Model" in data
    assert "write" in data["Model"]
    hook_label = _diag._label_hook(sample_hook, "PRE_HANDLER")
    assert data["Model"]["write"] == [
        f"PRE_TX:secdep:{secdep_label}",
        f"PRE_TX:dep:{dep_label}",
        "START_TX:hook:sys:txn:begin@START_TX",
        f"PRE_HANDLER:{hook_label}",
        "HANDLER:hook:sys:handler:crud@HANDLER",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]
    assert "read" in data["Model"]
    assert not any("hook:sys:txn:begin@START_TX" in s for s in data["Model"]["read"])


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

    def fake_flattened_order(
        plan,
        *,
        persist,
        include_system_steps,
        deps,
        secdeps,
        hooks,
    ):
        calls["flatten"] = True
        hook_label = _diag._label_hook(sample_hook, "PRE_HANDLER")
        assert hooks == {"PRE_HANDLER": [hook_label]}
        return [
            "START_TX:hook:sys:txn:begin@START_TX",
            f"PRE_HANDLER:{hook_label}",
            "PRE_HANDLER:atom:emit:paired_pre@emit:aliases:pre_flush",
            "HANDLER:hook:sys:handler:crud@HANDLER",
            "END_TX:hook:sys:txn:commit@END_TX",
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
    hook_label = _diag._label_hook(sample_hook, "PRE_HANDLER")
    assert data["Model"]["create"] == [
        "START_TX:hook:sys:txn:begin@START_TX",
        f"PRE_HANDLER:{hook_label}",
        "PRE_HANDLER:atom:emit:paired_pre@emit:aliases:pre_flush",
        "HANDLER:hook:sys:handler:crud@HANDLER",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]


@pytest.mark.asyncio
async def test_planz_endpoint_uses_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Subsequent calls should reuse cached plan data."""

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
    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    calls = {"flatten": 0}

    def fake_flattened_order(
        plan,
        *,
        persist,
        include_system_steps,
        deps,
        secdeps,
        hooks,
    ):
        calls["flatten"] += 1
        return []

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)

    await planz()
    await planz()

    assert calls["flatten"] == 1
