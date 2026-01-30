from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_system_endpoints_are_available(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        health = await client.get(f"{base_url}/healthz")
        kernel = await client.get(f"{base_url}/kernelz")
    assert health.status_code == 200
    assert health.json()["ok"] is True
    assert kernel.status_code == 200
    assert "Widget" in kernel.json()
