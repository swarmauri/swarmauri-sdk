import pytest
from types import SimpleNamespace
from time import perf_counter, sleep

from tigrbl.system.diagnostics import _build_hookz_endpoint
from tigrbl.system import diagnostics as _diag
from tigrbl import hook_ctx


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 5, 100])
async def test_hookz_performance(count):
    """Measure /system/hookz response time with varying hook counts."""

    class Model:
        __name__ = "Model"
        hooks = SimpleNamespace()
        rpc = SimpleNamespace(create=None)
        opspecs = SimpleNamespace(all=())

    # Generate ``count`` hooks on the POST_RESPONSE phase of "create"
    def make_hook(idx):
        @hook_ctx(ops="*", phase="POST_RESPONSE")
        def _hook(cls, ctx):
            return None

        _hook.__name__ = f"hook_{idx}"
        return _hook

    hooks = [make_hook(i) for i in range(count)]
    Model.hooks.create = SimpleNamespace(POST_RESPONSE=hooks)

    class API:
        models = {"Model": Model}

    hookz = _build_hookz_endpoint(API)

    start = perf_counter()
    data = await hookz()
    duration = perf_counter() - start

    assert len(data["Model"]["create"]["POST_RESPONSE"]) == count
    print(f"/system/hookz with {count} hooks took {duration:.6f}s")


@pytest.mark.asyncio
async def test_hookz_cached_call_faster(monkeypatch) -> None:
    """Second call should reuse cached data and skip expensive work."""

    class Model:
        __name__ = "Model"
        hooks = SimpleNamespace()
        rpc = SimpleNamespace(create=None)
        opspecs = SimpleNamespace(all=())

    # Create a single hook to keep output small
    @hook_ctx(ops="*", phase="POST_RESPONSE")
    def _hook(cls, ctx):
        return None

    Model.hooks.create = SimpleNamespace(POST_RESPONSE=[_hook])

    class API:
        models = {"Model": Model}

    calls = {"iter": 0}

    orig_model_iter = _diag._model_iter

    def slow_model_iter(api):
        calls["iter"] += 1
        sleep(0.01)
        return orig_model_iter(api)

    monkeypatch.setattr(_diag, "_model_iter", slow_model_iter)

    hookz = _build_hookz_endpoint(API)

    start = perf_counter()
    await hookz()
    first = perf_counter() - start

    start = perf_counter()
    await hookz()
    second = perf_counter() - start

    assert calls["iter"] == 1
    assert second < first * 0.05
    print(f"first={first:.6f}s second={second:.6f}s")
