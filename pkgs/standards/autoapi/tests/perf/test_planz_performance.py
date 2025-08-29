import time
from types import SimpleNamespace

import pytest
from autoapi.v3.system import diagnostics


def _make_api(count: int):
    class DummySpec:
        def __init__(self, alias: str):
            self.alias = alias
            self.target = "handler"
            self.persist = "default"

    class DummyModel:
        __name__ = "Model"
        opspecs = SimpleNamespace(all=[DummySpec(f"m{i}") for i in range(count)])

    api = SimpleNamespace(models={"Model": DummyModel})
    return api


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 5, 100])
async def test_planz_cache_performance(count: int, monkeypatch):
    api = _make_api(count)

    def fake_build_phase_chains(model, alias):
        def fn():
            return None

        return {ph: [fn for _ in range(10)] for ph in diagnostics.PHASES}

    monkeypatch.setattr(diagnostics, "build_phase_chains", fake_build_phase_chains)
    endpoint = diagnostics._build_planz_endpoint(api)

    start = time.perf_counter()
    await endpoint()
    first = time.perf_counter() - start

    start = time.perf_counter()
    result = await endpoint()
    second = time.perf_counter() - start

    assert second <= first
    assert len(result["Model"]) == count
    total_steps = sum(len(seq) for seq in result["Model"].values())
    assert total_steps >= count * len(diagnostics.PHASES) * 10
