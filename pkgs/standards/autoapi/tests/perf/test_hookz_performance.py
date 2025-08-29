import time
from types import SimpleNamespace

import pytest

from autoapi.v3.system.diagnostics import _build_hookz_endpoint
from autoapi.v3.opspec import OpSpec


@pytest.mark.asyncio
@pytest.mark.parametrize("op_count", [1, 5, 100])
async def test_hookz_cached_response(op_count: int) -> None:
    """Hookz endpoint should cache computed results."""

    class API:
        pass

    class Model:
        __name__ = "Widget"

    def noop(ctx):
        return None

    Model.opspecs = SimpleNamespace(
        all=tuple(
            OpSpec(alias=f"op{i}", target="create", table=Model)
            for i in range(op_count)
        )
    )

    hooks_root = SimpleNamespace()
    for i in range(op_count):
        alias_ns = SimpleNamespace(HANDLER=[noop])
        setattr(hooks_root, f"op{i}", alias_ns)
    Model.hooks = hooks_root

    api = API()
    api.models = {"Widget": Model}

    endpoint = _build_hookz_endpoint(api)

    start = time.perf_counter()
    await endpoint()
    first = time.perf_counter() - start

    start = time.perf_counter()
    await endpoint()
    second = time.perf_counter() - start

    assert second <= first
