from __future__ import annotations

import httpx
import pytest

from tigrbl_client import TigrblClient


@pytest.mark.asyncio
async def test_rest_and_rpc_ids_align(running_widget_app: str) -> None:
    base_url = running_widget_app

    async with httpx.AsyncClient() as http_client:
        rest = await http_client.post(f"{base_url}/widget", json={"name": "Mix"})
    rest_id = rest.json()["id"]

    client = TigrblClient(f"{base_url}/rpc")
    rpc = client.call("Widget.read", params={"id": rest_id})

    assert rpc["id"] == rest_id
