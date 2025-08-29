import time
from types import SimpleNamespace

import pytest

from autoapi.v3.system.diagnostics import _build_methodz_endpoint
from autoapi.v3.opspec import OpSpec


@pytest.mark.asyncio
@pytest.mark.parametrize("op_count", [1, 5, 100])
async def test_methodz_cached_response(op_count: int) -> None:
    """Methodz endpoint should cache computed results."""

    class API:
        pass

    class Model:
        __name__ = "Widget"

    def handler(ctx):
        return None

    Model.opspecs = SimpleNamespace(
        all=tuple(
            OpSpec(alias=f"op{i}", target="create", table=Model, handler=handler)
            for i in range(op_count)
        )
    )

    api = API()
    api.models = {"Widget": Model}

    endpoint = _build_methodz_endpoint(api)

    start = time.perf_counter()
    await endpoint()
    first = time.perf_counter() - start

    start = time.perf_counter()
    await endpoint()
    second = time.perf_counter() - start

    assert second <= first
