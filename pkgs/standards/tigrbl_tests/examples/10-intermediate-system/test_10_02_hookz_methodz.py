from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_hookz_and_methodz_endpoints(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        hookz = await client.get(f"{base_url}/hookz")
        methodz = await client.get(f"{base_url}/methodz")
    assert hookz.status_code == 200
    assert methodz.status_code == 200
    assert "Widget" in hookz.json()
    assert "Widget" in methodz.json()
