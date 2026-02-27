from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_tigrbl_dispatch_exports_removed() -> None:
    import tigrbl

    assert not hasattr(tigrbl, "dispatch_operation")
    assert not hasattr(tigrbl, "resolve_operation")
