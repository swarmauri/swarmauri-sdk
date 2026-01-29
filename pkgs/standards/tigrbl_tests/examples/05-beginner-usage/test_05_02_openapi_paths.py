from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_openapi_includes_widget_paths(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/widget" in paths
    assert "/widget/{id}" in paths
