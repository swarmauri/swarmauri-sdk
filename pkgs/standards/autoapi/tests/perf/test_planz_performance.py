import time
from types import SimpleNamespace

import pytest

from autoapi.v3.system.diagnostics import _build_planz_endpoint
from autoapi.v3.opspec import OpSpec
from autoapi.v3.runtime import plan as _plan


@pytest.mark.asyncio
@pytest.mark.parametrize("op_count", [1, 5, 100])
async def test_planz_cached_response(
    monkeypatch: pytest.MonkeyPatch, op_count: int
) -> None:
    """Planz endpoint should cache computed results even for large plans."""

    class API:
        pass

    class Model:
        __name__ = "Widget"

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
            for i in range(op_count)
        )
    )

    dummy_plan = object()
    Model.runtime = SimpleNamespace(plan=dummy_plan)

    def fake_flattened_order(plan, *, persist, include_system_steps, deps):
        return [f"step{j}" for j in range(1000)]

    monkeypatch.setattr(_plan, "flattened_order", fake_flattened_order)

    api = API()
    api.models = {"Widget": Model}

    endpoint = _build_planz_endpoint(api)

    start = time.perf_counter()
    await endpoint()
    first = time.perf_counter() - start

    start = time.perf_counter()
    await endpoint()
    second = time.perf_counter() - start

    assert second <= first
