from __future__ import annotations

import pytest

from tigrbl_client import TigrblClient


@pytest.mark.asyncio
async def test_async_client_get(running_widget_app: str) -> None:
    base_url = running_widget_app
    client = TigrblClient(base_url)
    created = client.post("/widget", data={"name": "Async"})
    item_id = created["id"]
    response = await client.aget(f"/widget/{item_id}")
    assert response["name"] == "Async"
