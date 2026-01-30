from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_hookz_endpoint_lists_hooks(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        hookz = await client.get(f"{base_url}/hookz")
    assert hookz.status_code == 200
    assert "Widget" in hookz.json()
