from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_kernelz_endpoint_lists_phases(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        kernel = await client.get(f"{base_url}/kernelz")
    assert kernel.status_code == 200
    assert "Widget" in kernel.json()
