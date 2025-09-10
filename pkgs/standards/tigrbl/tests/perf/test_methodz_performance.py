import pytest
from types import SimpleNamespace
from time import perf_counter, sleep

from tigrbl.system.diagnostics import _build_methodz_endpoint
from tigrbl.system import diagnostics as _diag
from tigrbl.op import OpSpec


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 5, 100])
async def test_methodz_performance(count):
    """Measure /system/methodz response time with varying method counts."""

    class Model:
        __name__ = "Model"

    def handler(ctx):
        return None

    # Generate ``count`` OpSpec instances for the model
    Model.opspecs = SimpleNamespace(
        all=tuple(
            OpSpec(
                alias=f"op{i}",
                target="create",
                table=Model,
                persist="default",
                handler=handler,
            )
            for i in range(count)
        )
    )

    class API:
        models = {"Model": Model}

    methodz = _build_methodz_endpoint(API)

    start = perf_counter()
    data = await methodz()
    duration = perf_counter() - start

    # Basic sanity checks
    assert len(data["methods"]) == count

    # Capture duration for performance tracking
    print(f"/system/methodz with {count} methods took {duration:.6f}s")


@pytest.mark.asyncio
async def test_methodz_cached_call_faster(monkeypatch) -> None:
    """Subsequent calls should bypass expensive computation via cache."""

    class Model:
        __name__ = "Model"

    def handler(ctx):
        return None

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

    class API:
        models = {"Model": Model}

    calls = {"ops": 0}

    orig_opspecs = _diag._opspecs

    def slow_opspecs(model):
        calls["ops"] += 1
        sleep(0.01)
        return orig_opspecs(model)

    monkeypatch.setattr(_diag, "_opspecs", slow_opspecs)

    methodz = _build_methodz_endpoint(API)

    start = perf_counter()
    await methodz()
    first = perf_counter() - start

    start = perf_counter()
    await methodz()
    second = perf_counter() - start

    assert calls["ops"] == 1
    assert second < first * 0.05
    print(f"first={first:.6f}s second={second:.6f}s")
