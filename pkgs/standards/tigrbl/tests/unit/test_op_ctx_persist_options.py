import pytest
from types import SimpleNamespace

from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.op import op_ctx
from tigrbl.bindings import handlers
from tigrbl.system import diagnostics as _diag


def _build_model(persist: str):
    class Model:
        __name__ = "Model"

        @op_ctx(alias="create", target="create", persist=persist)
        def custom(cls, ctx):  # pragma: no cover - execution not needed
            return None

    specs = mro_collect_decorated_ops(Model)
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

    def fake_build(model, alias):
        return {"HANDLER": Model.hooks.create.HANDLER}

    monkeypatch.setattr(_diag._default_kernel, "build", fake_build)

    api = SimpleNamespace(models={"Model": Model})
    kernelz = _diag._build_kernelz_endpoint(api)
    data = await kernelz()
    seq = data["Model"]["create"]

    chain_steps = Model.hooks.create.HANDLER
    step_map = {fn.__name__: fn for fn in chain_steps}
    custom_step = step_map.get("custom")
    core_step = step_map.get("create")
    custom_label = _diag._label_hook(custom_step, "HANDLER") if custom_step else None
    core_label = _diag._label_hook(core_step, "HANDLER") if core_step else None
    custom_pref = f"HANDLER:{custom_label}" if custom_label else None
    core_pref = f"HANDLER:{core_label}" if core_label else None

    expected_seq: list[str] = []
    if persist != "skip":
        expected_seq.append("START_TX:hook:sys:txn:begin@START_TX")
        if persist == "append" and core_pref is not None and custom_pref is not None:
            expected_seq.extend([core_pref, custom_pref])
        else:
            seq_items = [custom_pref]
            if core_pref is not None:
                seq_items.append(core_pref)
            expected_seq.extend([s for s in seq_items if s])
        expected_seq.append("END_TX:hook:sys:txn:commit@END_TX")
    else:
        expected_seq.append(custom_pref)

    assert seq == [s for s in expected_seq if s]
