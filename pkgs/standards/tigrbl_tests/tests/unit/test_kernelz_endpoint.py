import pytest
from types import SimpleNamespace

from tigrbl.op import OpSpec
from tigrbl.system import diagnostics as _diag
from tigrbl.system.diagnostics import _build_kernelz_endpoint


def sample_hook(ctx):
    return None


def sample_atom(ctx):
    return None


sample_atom.__tigrbl_label = "atom:test:step@resolve:values"


def handler(ctx):
    return None


@pytest.mark.asyncio
async def test_kernelz_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    class API:
        pass

    class Model:
        __name__ = "Model"

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

    api = API()
    api.models = {"Model": Model}

    def fake_build(model, alias):
        assert model is Model and alias == "create"
        return {"PRE_HANDLER": [sample_atom, sample_hook], "HANDLER": [handler]}

    monkeypatch.setattr(_diag._default_kernel, "build", fake_build)

    kernelz = _build_kernelz_endpoint(api)
    data = await kernelz()

    assert "Model" in data
    assert "create" in data["Model"]
    seq = data["Model"]["create"]
    assert seq == [
        "START_TX:hook:sys:txn:begin@START_TX",
        f"PRE_HANDLER:{_diag._label_hook(sample_atom, 'PRE_HANDLER')}",
        f"PRE_HANDLER:{_diag._label_hook(sample_hook, 'PRE_HANDLER')}",
        f"HANDLER:{_diag._label_hook(handler, 'HANDLER')}",
        "END_TX:hook:sys:txn:commit@END_TX",
    ]
