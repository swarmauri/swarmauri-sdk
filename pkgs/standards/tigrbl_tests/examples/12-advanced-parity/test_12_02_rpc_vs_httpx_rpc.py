from __future__ import annotations

import httpx
import pytest

from tigrbl_client import TigrblClient


@pytest.mark.asyncio
async def test_rpc_parity_with_httpx(running_widget_app: str) -> None:
    base_url = running_widget_app
    client = TigrblClient(f"{base_url}/rpc")

    rpc_result = client.call("Widget.create", params={"name": "RPC"})

    async with httpx.AsyncClient() as http_client:
        payload = {
            "jsonrpc": "2.0",
            "method": "Widget.create",
            "params": {"name": "RPC"},
            "id": "1",
        }
        http_result = await http_client.post(f"{base_url}/rpc", json=payload)

    assert http_result.status_code == 200
    assert http_result.json()["result"]["name"] == rpc_result["name"]
