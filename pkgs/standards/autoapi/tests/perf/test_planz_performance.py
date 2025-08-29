import pytest
from types import SimpleNamespace
from time import perf_counter

from autoapi.v3.system.diagnostics import _build_planz_endpoint
from autoapi.v3.opspec import OpSpec
from autoapi.v3.runtime import plan as _plan


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 5, 100])
async def test_planz_performance(monkeypatch, count):
    """Measure /system/planz response time with varying operation counts."""

    class Model:
        __name__ = "Model"

    def handler(ctx):
        return None

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
    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    def fake_flattened_order(plan, *, persist, include_system_steps, deps):
        return [f"step_{i}" for i in range(10)]

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)

    class API:
        models = {"Model": Model}

    planz = _build_planz_endpoint(API)

    start = perf_counter()
    data = await planz()
    duration = perf_counter() - start

    total_steps = sum(len(v) for v in data["Model"].values())
    assert total_steps == count * 10
    print(f"/system/planz with {count} operations took {duration:.6f}s")
