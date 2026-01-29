from __future__ import annotations

import httpx
import pytest

from tigrbl_client import TigrblClient


@pytest.mark.asyncio
async def test_rest_and_client_rest_match(running_widget_app: str) -> None:
    base_url = running_widget_app
    client = TigrblClient(base_url)

    async with httpx.AsyncClient() as http_client:
        rest = await http_client.post(
            f"{base_url}/widget",
            json={"name": "Parity"},
        )
    assert rest.status_code == 201
    client_result = client.post("/widget", data={"name": "Parity"})
    assert client_result["name"] == "Parity"
