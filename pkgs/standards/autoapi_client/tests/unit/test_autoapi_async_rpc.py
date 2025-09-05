from unittest.mock import patch

import json
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_acall_status_code():
    """Ensure status code is returned and JSON parses correctly."""

    async def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            201, request=request, json={"jsonrpc": "2.0", "result": {"value": 1}}
        )

    with patch.object(httpx.AsyncClient, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result, status = await client.acall("test.method", status_code=True)

    assert result == {"value": 1}
    assert status == 201


@pytest.mark.unit
@pytest.mark.asyncio
async def test_acall_no_raise_on_http_error():
    """Verify raise_status=False returns response on HTTP errors."""

    async def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            500, request=request, json={"jsonrpc": "2.0", "result": {"error": True}}
        )

    with patch.object(httpx.AsyncClient, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result, status = await client.acall(
            "test.method", status_code=True, raise_status=False
        )

    assert result == {"error": True}
    assert status == 500


@pytest.mark.unit
@pytest.mark.asyncio
async def test_acall_invalid_json_propagates():
    """Invalid JSON should propagate JSON errors."""

    async def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(200, request=request, content=b"not-json")

    with patch.object(httpx.AsyncClient, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        with pytest.raises(json.JSONDecodeError):
            await client.acall("test.method")
