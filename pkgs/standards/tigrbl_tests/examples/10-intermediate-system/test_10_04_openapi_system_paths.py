from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_openapi_system_paths(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/openapi.json")
    paths = response.json()["paths"]
    assert "/healthz" in paths
    assert "/kernelz" in paths
    assert "/systemz/healthz" in paths
