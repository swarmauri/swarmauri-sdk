from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_systemz_prefix_routes(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/systemz/healthz")
    assert response.status_code == 200
    assert response.json()["ok"] is True
