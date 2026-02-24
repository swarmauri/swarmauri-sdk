import time
import pytest

from tigrbl import core as _core
from tigrbl.bindings.handlers.steps import _wrap_core


@pytest.mark.asyncio
@pytest.mark.unit
async def test_wrap_core_create_dispatch(monkeypatch):
    class Model:
        pass

    called = {}

    async def fake_create(model, payload, db=None):
        called["model"] = model
        called["payload"] = payload
        called["db"] = db
        return {"ok": True}

    monkeypatch.setattr(_core, "create", fake_create)
    step = _wrap_core(Model, "create")
    ctx = {"db": 123, "payload": {"a": 1}}
    result = await step(ctx)
    assert result == {"ok": True}
    assert called == {"model": Model, "payload": {"a": 1}, "db": 123}


@pytest.mark.perf
def test_wrap_core_cache_hits():
    class Model:
        pass

    _wrap_core.cache_clear()
    _wrap_core(Model, "create")
    info = _wrap_core.cache_info()
    assert info.misses == 1
    assert info.hits == 0
    _wrap_core(Model, "create")
    info = _wrap_core.cache_info()
    assert info.hits == 1
    assert info.misses == 1


@pytest.mark.perf
def test_wrap_core_cached_speed():
    class Model:
        pass

    iterations = 1000

    _wrap_core.cache_clear()
    start = time.perf_counter()
    for i in range(iterations):
        _wrap_core(type(f"M{i}", (), {}), "create")
    uncached = time.perf_counter() - start

    _wrap_core.cache_clear()
    _wrap_core(Model, "create")
    start = time.perf_counter()
    for _ in range(iterations):
        _wrap_core(Model, "create")
    cached = time.perf_counter() - start

    print(f"uncached={uncached:.6f}s cached={cached:.6f}s")
    assert cached < uncached / 5
