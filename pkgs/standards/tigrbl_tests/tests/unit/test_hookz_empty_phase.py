from types import SimpleNamespace

import pytest

from tigrbl.system.diagnostics import _build_hookz_endpoint


@pytest.mark.asyncio
async def test_hookz_omits_empty_phases_and_operations():
    """Hookz should skip phases without hooks and drop empty operations."""

    def dummy(ctx):
        pass

    class API:
        pass

    class Model:
        pass

    Model.__name__ = "Model"
    Model.hooks = SimpleNamespace(
        foo=SimpleNamespace(PRE_TX_BEGIN=[dummy], POST_RESPONSE=[]),
        bar=SimpleNamespace(),
    )
    Model.rpc = SimpleNamespace(foo=None, bar=None)

    api = API()
    api.models = {"Model": Model}

    hookz = _build_hookz_endpoint(api)
    data = await hookz()

    assert "Model" in data
    assert "foo" in data["Model"]
    assert "POST_RESPONSE" not in data["Model"]["foo"]
    assert "bar" not in data["Model"]
