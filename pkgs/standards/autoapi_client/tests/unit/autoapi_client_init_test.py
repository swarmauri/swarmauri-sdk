import pytest
import httpx
from autoapi_client import AutoAPIClient


@pytest.mark.unit
def test_init_sets_properties():
    client = AutoAPIClient("https://example.com")
    assert client._endpoint == "https://example.com"
    assert client._own_sync is True
    assert client._own_async is True
    assert isinstance(client._client, httpx.Client)
    assert client._async_client is None


@pytest.mark.unit
def test_init_uses_provided_client():
    mock_client = httpx.Client()
    try:
        client = AutoAPIClient("https://example.com", client=mock_client)
        assert client._client is mock_client
        assert client._own_sync is False
        assert client._own_async is True
    finally:
        mock_client.close()


@pytest.mark.unit
def test_init_uses_provided_async_client():
    mock_async_client = httpx.AsyncClient()
    try:
        client = AutoAPIClient("https://example.com", async_client=mock_async_client)
        assert client._async_client is mock_async_client
        assert client._own_async is False
        assert client._own_sync is True
    finally:
        import asyncio

        asyncio.run(mock_async_client.aclose())


@pytest.mark.unit
def test_init_uses_both_provided_clients():
    mock_client = httpx.Client()
    mock_async_client = httpx.AsyncClient()
    try:
        client = AutoAPIClient(
            "https://example.com", client=mock_client, async_client=mock_async_client
        )
        assert client._client is mock_client
        assert client._async_client is mock_async_client
        assert client._own_sync is False
        assert client._own_async is False
    finally:
        mock_client.close()
        import asyncio

        asyncio.run(mock_async_client.aclose())
