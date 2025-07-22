import pytest
from autoapi_client import AutoAPIClient
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.unit
def test_enter_returns_self():
    client = AutoAPIClient("http://example.com")
    with client as ctx:
        assert ctx is client


@pytest.mark.unit
def test_exit_closes_owned_client():
    client = AutoAPIClient("http://example.com")
    client._client.close = MagicMock()
    with client:
        pass
    client._client.close.assert_called_once_with()


@pytest.mark.unit
def test_close_does_not_close_unowned_client():
    mock = MagicMock()
    client = AutoAPIClient("http://example.com", client=mock)
    client.close()
    mock.close.assert_not_called()


@pytest.mark.unit
def test_close_closes_owned_sync_client():
    client = AutoAPIClient("http://example.com")
    client._client.close = MagicMock()
    client.close()
    client._client.close.assert_called_once_with()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_enter_returns_self():
    client = AutoAPIClient("http://example.com")
    async with client as ctx:
        assert ctx is client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_exit_closes_owned_async_client():
    mock_async_client = AsyncMock()
    client = AutoAPIClient("http://example.com")
    client._async_client = mock_async_client
    client._own_async = True

    async with client:
        pass

    mock_async_client.aclose.assert_called_once_with()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aclose_does_not_close_unowned_async_client():
    mock_async_client = AsyncMock()
    client = AutoAPIClient("http://example.com", async_client=mock_async_client)
    await client.aclose()
    mock_async_client.aclose.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aclose_closes_owned_async_client():
    client = AutoAPIClient("http://example.com")
    mock_async_client = AsyncMock()
    client._async_client = mock_async_client
    client._own_async = True

    await client.aclose()
    mock_async_client.aclose.assert_called_once_with()
