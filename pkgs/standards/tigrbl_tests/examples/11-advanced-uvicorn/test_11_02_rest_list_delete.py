from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_rest_list_and_delete(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        await client.post(f"{base_url}/widget", json={"name": "One"})
        await client.post(f"{base_url}/widget", json={"name": "Two"})
        listing = await client.get(f"{base_url}/widget")
        assert listing.status_code == 200
        assert len(listing.json()) >= 2
        clear = await client.delete(f"{base_url}/widget")
        assert clear.status_code == 200
