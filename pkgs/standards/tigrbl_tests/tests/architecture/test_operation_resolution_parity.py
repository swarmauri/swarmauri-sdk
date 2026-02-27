from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_runtime_dispatch_module_is_fast_break_only():
    from tigrbl import dispatch_operation, resolve_operation

    with pytest.raises(RuntimeError, match="runtime-owned"):
        dispatch_operation(router=None)

    with pytest.raises(RuntimeError, match="runtime-owned"):
        resolve_operation(router=None)
