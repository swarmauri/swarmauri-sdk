import pytest
from types import SimpleNamespace
from time import perf_counter

from autoapi.v3.system.diagnostics import _build_methodz_endpoint
from autoapi.v3.opspec import OpSpec


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
