import pytest
from types import SimpleNamespace

from autoapi.v3.decorators import collect_decorated_ops, op_ctx
from autoapi.v3.bindings import handlers
from autoapi.v3.system import diagnostics as _diag


def _build_model(persist: str):
    class Model:
        __name__ = "Model"

        @op_ctx(alias="create", target="create", persist=persist)
        def custom(cls, ctx):  # pragma: no cover - execution not needed
            return None

    specs = collect_decorated_ops(Model)
    Model.opspecs = SimpleNamespace(all=tuple(specs))
    handlers.build_and_attach(Model, specs)
    return Model


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "persist, expected_chain",
    [
        ("default", ["custom", "create"]),
        ("prepend", ["custom", "create"]),
        ("append", ["create", "custom"]),
        ("override", ["custom"]),
        ("skip", ["custom"]),
    ],
)
async def test_op_ctx_persist_options(
    monkeypatch: pytest.MonkeyPatch, persist: str, expected_chain: list[str]
) -> None:
    Model = _build_model(persist)
    chain = [fn.__name__ for fn in Model.hooks.create.HANDLER]
    assert chain == expected_chain

    def fake_build_phase_chains(model, alias):
        return {"HANDLER": Model.hooks.create.HANDLER}

    monkeypatch.setattr(_diag, "build_phase_chains", fake_build_phase_chains)

    api = SimpleNamespace(models={"Model": Model})
    planz = _diag._build_planz_endpoint(api)
    data = await planz()
    seq = data["Model"]["create"]

    chain_steps = Model.hooks.create.HANDLER
    step_map = {fn.__name__: fn for fn in chain_steps}
    custom_step = step_map.get("custom")
    core_step = step_map.get("create")
    custom_label = _diag._label_hook(custom_step, "HANDLER") if custom_step else None
    core_label = _diag._label_hook(core_step, "HANDLER") if core_step else None

    expected_seq: list[str] = []
    if persist != "skip":
        expected_seq.append("sys:txn:begin@START_TX")
        if persist not in {"override"} and core_label is not None:
            expected_seq.append("sys:handler:crud@HANDLER")
        if persist == "append" and core_label is not None:
            expected_seq.extend([core_label, custom_label])
        else:
            expected_seq.extend([custom_label] + ([core_label] if core_label else []))
        expected_seq.append("sys:txn:commit@END_TX")
    else:
        expected_seq.append(custom_label)

    assert seq == expected_seq
