import pytest
from types import SimpleNamespace

from autoapi.v3.op import OpSpec
from autoapi.v3.system import diagnostics as _diag
from autoapi.v3.system.diagnostics import _build_kernelz_endpoint


def sample_hook(ctx):
    return None


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

    def fake_build_phase_chains(model, alias):
        assert model is Model and alias == "create"
        return {"PRE_HANDLER": [sample_hook], "HANDLER": [handler]}

    monkeypatch.setattr(_diag, "build_phase_chains", fake_build_phase_chains)

    kernelz = _build_kernelz_endpoint(api)
    data = await kernelz()

    assert "Model" in data
    assert "create" in data["Model"]
    phases = data["Model"]["create"]
    assert phases["PRE_HANDLER"] == [_diag._label_hook(sample_hook, "PRE_HANDLER")]
    assert phases["HANDLER"] == [_diag._label_hook(handler, "HANDLER")]
