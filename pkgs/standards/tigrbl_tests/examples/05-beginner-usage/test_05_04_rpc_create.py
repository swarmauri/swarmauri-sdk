from __future__ import annotations

import pytest

from tigrbl_client import TigrblClient


@pytest.mark.asyncio
async def test_rpc_create_via_client(running_widget_app: str) -> None:
    base_url = running_widget_app
    client = TigrblClient(f"{base_url}/rpc")
    result = client.call("Widget.create", params={"name": "Bravo"})
    assert result["name"] == "Bravo"
