import pytest
from types import SimpleNamespace

from autoapi.v3.system.diagnostics import _build_planz_endpoint
from autoapi.v3.opspec import OpSpec


@pytest.mark.asyncio
async def test_planz_endpoint_sequence():
    class API:
        pass

    class Model:
        __name__ = "Model"

    def start_tx(ctx):
        pass

    start_tx.__name__ = "start_tx"

    def end_tx(ctx):
        pass

    end_tx.__name__ = "end_tx"

    def mark_skip(ctx):
        pass

    mark_skip.__name__ = "mark_skip_persist"

    Model.hooks = SimpleNamespace(
        write=SimpleNamespace(START_TX=[start_tx], END_TX=[end_tx]),
        read=SimpleNamespace(PRE_TX_BEGIN=[mark_skip]),
    )
    Model.opspecs = SimpleNamespace(
        all=(
            OpSpec(alias="write", target="create", table=Model, persist="default"),
            OpSpec(alias="read", target="read", table=Model, persist="skip"),
        )
    )

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)
    data = await planz()

    assert "Model" in data
    assert "write" in data["Model"]
    assert any("start_tx" in s for s in data["Model"]["write"])
    assert "read" in data["Model"]
    assert not any("start_tx" in s for s in data["Model"]["read"])
