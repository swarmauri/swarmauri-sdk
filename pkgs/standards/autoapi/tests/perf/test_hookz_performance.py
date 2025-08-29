import pytest
from types import SimpleNamespace
from time import perf_counter

from autoapi.v3.system.diagnostics import _build_hookz_endpoint
from autoapi.v3 import hook_ctx


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
