import pytest
from autoapi_client import AutoAPIClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_context_manages_session():
    client = AutoAPIClient("http://example.com")
    assert not client._async_client.is_closed

    async with AutoAPIClient("http://example.com") as ctx:
        assert ctx is not None
        assert not ctx._async_client.is_closed

    assert ctx._async_client.is_closed


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aclose_closes_async_client():
    client = AutoAPIClient("http://example.com")
    await client.aclose()
    assert client._async_client.is_closed
