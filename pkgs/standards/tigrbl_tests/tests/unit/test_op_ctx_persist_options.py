import pytest
from types import SimpleNamespace

from tests.conftest import build_and_attach, mro_collect_decorated_ops
from tigrbl.decorators.op import op_ctx
from tigrbl.system import diagnostics as _diag


def _build_model(persist: str):
    class Model:
        __name__ = "Model"

        @op_ctx(alias="create", target="create", persist=persist)
        def custom(cls, ctx):  # pragma: no cover - execution not needed
            return None

    specs = mro_collect_decorated_ops(Model)
    Model.opspecs = SimpleNamespace(all=tuple(specs))
    build_and_attach(Model, specs)
    return Model


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "persist, expect_tx",
    [
        ("default", True),
        ("prepend", True),
        ("append", True),
        ("override", True),
        ("skip", False),
    ],
)
async def test_op_ctx_persist_options(
    monkeypatch: pytest.MonkeyPatch, persist: str, expect_tx: bool
) -> None:
    Model = _build_model(persist)
    chain = [fn.__name__ for fn in Model.hooks.create.HANDLER]
    assert chain == ["_default_handler_step"]

    def fake_build(model, alias):
        return {"HANDLER": Model.hooks.create.HANDLER}

    monkeypatch.setattr(_diag._default_kernel, "_build_op", fake_build)

    router = SimpleNamespace(tables={"Model": Model})
    kernelz = _diag._build_kernelz_endpoint(router)
    data = await kernelz()
    seq = data["Model"]["create"]

    chain_steps = Model.hooks.create.HANDLER
    core_label = _diag._label_hook(chain_steps[0], "HANDLER") if chain_steps else None
    core_pref = f"HANDLER:{core_label}" if core_label else None

    expected_seq: list[str] = []
    if expect_tx:
        expected_seq.append("START_TX:hook:sys:txn:begin@START_TX")
    if core_pref is not None:
        expected_seq.append(core_pref)
    if expect_tx:
        expected_seq.append("END_TX:hook:sys:txn:commit@END_TX")

    assert seq == [s for s in expected_seq if s]
