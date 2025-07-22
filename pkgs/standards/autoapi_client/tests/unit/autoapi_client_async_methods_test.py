import json
from unittest.mock import patch, AsyncMock

import httpx
import pytest

from autoapi_client import AutoAPIClient


class DummySchema:
    def __init__(self, **data):
        self._data = data

    @classmethod
    def model_validate(cls, data):
        return cls(**data)

    def model_dump_json(self):
        return json.dumps(self._data)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_request():
    captured = {}

    async def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params, headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"id": 1, "name": "test"})

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget("/users/1")

    assert captured["url"] == "/users/1"
    assert result == {"id": 1, "name": "test"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_request_with_params():
    captured = {}

    async def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params, headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"results": []})

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget("/users", params={"page": 1, "limit": 10})

    assert captured["params"] == {"page": 1, "limit": 10}
    assert result == {"results": []}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apost_request():
    captured = {}

    async def fake_post(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 2, "name": "new user"})

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "post", new=fake_post):
        result = await client.apost(
            "/users", params={"name": "new user", "email": "test@example.com"}
        )

    assert captured["json"] == {"name": "new user", "email": "test@example.com"}
    assert result == {"id": 2, "name": "new user"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aput_request():
    captured = {}

    async def fake_put(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("PUT", url)
        return httpx.Response(
            200, request=request, json={"id": 1, "name": "updated user"}
        )

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "put", new=fake_put):
        result = await client.aput("/users/1", params={"name": "updated user"})

    assert captured["json"] == {"name": "updated user"}
    assert result == {"id": 1, "name": "updated user"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apatch_request():
    captured = {}

    async def fake_patch(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("PATCH", url)
        return httpx.Response(
            200, request=request, json={"id": 1, "name": "patched user"}
        )

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "patch", new=fake_patch):
        result = await client.apatch("/users/1", params={"name": "patched user"})

    assert captured["json"] == {"name": "patched user"}
    assert result == {"id": 1, "name": "patched user"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_adelete_request():
    captured = {}

    async def fake_delete(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("DELETE", url)
        return httpx.Response(204, request=request, content=b"")

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "delete", new=fake_delete):
        result = await client.adelete("/users/1")

    assert captured["url"] == "/users/1"
    assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_custom_headers():
    captured = {}

    async def fake_get(self, url, *, params=None, headers=None):
        captured.update(headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"data": "test"})

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget(
            "/test", headers={"Authorization": "Bearer token", "Custom": "value"}
        )

    assert "Authorization" in captured["headers"]
    assert captured["headers"]["Authorization"] == "Bearer token"
    assert captured["headers"]["Custom"] == "value"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result == {"data": "test"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_schema_params():
    schema = DummySchema(name="John", email="john@example.com")
    captured = {}

    async def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1})

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "post", new=fake_post):
        result = await client.apost("/users", params=schema)

    assert captured["json"] == {"name": "John", "email": "john@example.com"}
    assert result == {"id": 1}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_schema_output():
    async def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(
            200, request=request, json={"name": "John", "email": "john@example.com"}
        )

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget("/users/1", out_schema=DummySchema)

    assert isinstance(result, DummySchema)
    assert result._data["name"] == "John"
    assert result._data["email"] == "john@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_empty_response_handling():
    async def fake_delete(self, url, *, json=None, headers=None):
        request = httpx.Request("DELETE", url)
        return httpx.Response(204, request=request, content=b"")

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "delete", new=fake_delete):
        result = await client.adelete("/users/1")

    assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_text_response_handling():
    async def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, content=b"plain text response")

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget("/text")

    assert result == "plain text response"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_unsupported_method():
    client = AutoAPIClient("http://example.com")

    with pytest.raises(ValueError, match="Unsupported HTTP method: INVALID"):
        await client._amake_request("INVALID", "/test")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_http_error_handling():
    async def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        response = httpx.Response(404, request=request, json={"error": "Not found"})

        # Mock raise_for_status to raise an exception
        def mock_raise_for_status():
            raise httpx.HTTPStatusError("Not found", request=request, response=response)

        response.raise_for_status = mock_raise_for_status
        return response

    client = AutoAPIClient("http://example.com")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        with pytest.raises(httpx.HTTPStatusError):
            await client.aget("/nonexistent")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_client_creation():
    """Test that async client is created on demand."""
    client = AutoAPIClient("http://example.com")
    assert client._async_client is None

    # Mock the AsyncClient creation
    with patch("httpx.AsyncClient") as mock_async_client:
        mock_instance = AsyncMock()
        mock_async_client.return_value = mock_instance
        # Create a proper response with a request
        request = httpx.Request("GET", "/test")
        response = httpx.Response(200, json={}, request=request)
        mock_instance.get = AsyncMock(return_value=response)

        await client.aget("/test")

        # Check that AsyncClient was created
        mock_async_client.assert_called_once_with(timeout=10.0)
        assert client._own_async is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_url_none_uses_endpoint():
    captured = {}

    async def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={})

    client = AutoAPIClient("http://example.com/api")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget()  # No URL provided

    assert captured["url"] == "http://example.com/api"
    assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_url_provided_overrides_endpoint():
    captured = {}

    async def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={})

    client = AutoAPIClient("http://example.com/api")
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        result = await client.aget("/custom/path")

    assert captured["url"] == "/custom/path"
    assert result == {}
