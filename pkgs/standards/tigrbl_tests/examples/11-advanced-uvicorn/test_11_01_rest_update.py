from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_rest_update_round_trip(running_widget_app: str) -> None:
    base_url = running_widget_app
    async with httpx.AsyncClient() as client:
        create = await client.post(f"{base_url}/widget", json={"name": "Gamma"})
        item_id = create.json()["id"]
        update = await client.patch(
            f"{base_url}/widget/{item_id}",
            json={"name": "Delta"},
        )
        assert update.status_code == 200
        assert update.json()["name"] == "Delta"
