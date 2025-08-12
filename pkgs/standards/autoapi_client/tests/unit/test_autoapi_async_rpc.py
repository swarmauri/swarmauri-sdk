from unittest.mock import patch

import httpx
import pytest

from autoapi_client import AutoAPIClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_acall_basic():
    """Test basic async RPC call functionality."""
    captured = {}

    async def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json, url=url, headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": {"success": True}}
        )

    with patch.object(httpx.AsyncClient, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result = await client.acall("test.method")

    assert captured["json"]["jsonrpc"] == "2.0"
    assert captured["json"]["method"] == "test.method"
    assert captured["json"]["params"] == {}
    assert "id" in captured["json"]
    assert captured["url"] == "http://example.com/api"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result == {"success": True}
