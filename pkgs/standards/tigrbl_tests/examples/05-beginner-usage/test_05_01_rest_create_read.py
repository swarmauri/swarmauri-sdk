from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_rest_create_and_read(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        create = await client.post(f"{base_url}/widget", json={"name": "Alpha"})
        assert create.status_code == 201
        item_id = create.json()["id"]
        read = await client.get(f"{base_url}/widget/{item_id}")
        assert read.status_code == 200
        assert read.json()["name"] == "Alpha"
