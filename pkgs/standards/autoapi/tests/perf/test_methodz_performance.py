import time
from types import SimpleNamespace

import pytest
from autoapi.v3.system import diagnostics


def _make_api(count: int):
    class DummySpec:
        def __init__(self, alias: str):
            self.alias = alias
            self.target = f"handler_{alias}"
            self.arity = 1
            self.persist = "default"
            self.request_model = None
            self.response_model = None
            self.expose_routes = True
            self.expose_rpc = True
            self.tags = ()

    class DummyModel:
        __name__ = "Model"
        opspecs = SimpleNamespace(all=[DummySpec(f"m{i}") for i in range(count)])

    api = SimpleNamespace(models={"Model": DummyModel})
    return api


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 5, 100])
async def test_methodz_cache_performance(count: int):
    api = _make_api(count)
    endpoint = diagnostics._build_methodz_endpoint(api)

    start = time.perf_counter()
    await endpoint()
    first = time.perf_counter() - start

    start = time.perf_counter()
    result = await endpoint()
    second = time.perf_counter() - start

    assert second <= first
    assert len(result["methods"]) == count
