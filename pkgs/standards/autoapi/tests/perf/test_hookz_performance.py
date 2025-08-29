import time
from types import SimpleNamespace

import pytest
from autoapi.v3.system import diagnostics


def _make_api(count: int):
    def dummy_fn():
        pass

    class DummySpec:
        def __init__(self, alias: str):
            self.alias = alias

    hooks_root = SimpleNamespace()
    rpc_ns = {}
    for i in range(count):
        alias = f"m{i}"
        rpc_ns[alias] = None
        setattr(
            hooks_root,
            alias,
            SimpleNamespace(HANDLER=[dummy_fn]),
        )

    class DummyModel:
        __name__ = "Model"
        opspecs = SimpleNamespace(all=[DummySpec(f"m{i}") for i in range(count)])
        hooks = hooks_root
        rpc = SimpleNamespace(**rpc_ns)

    api = SimpleNamespace(models={"Model": DummyModel})
    return api


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 5, 100])
async def test_hookz_cache_performance(count: int):
    api = _make_api(count)
    endpoint = diagnostics._build_hookz_endpoint(api)

    start = time.perf_counter()
    await endpoint()
    first = time.perf_counter() - start

    start = time.perf_counter()
    result = await endpoint()
    second = time.perf_counter() - start

    assert second <= first
    assert len(result["Model"]) == count
