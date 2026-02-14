import pytest

import httpx

from swarmauri_canon_http import HttpClient


def test_httpx_async_http_transport_exists_and_is_constructible():
    transport = httpx.AsyncHTTPTransport()
    assert isinstance(transport, httpx.AsyncHTTPTransport)


@pytest.mark.asyncio
async def test_httpx_async_client_accepts_custom_async_transport():
    transport = httpx.AsyncHTTPTransport()
    client = httpx.AsyncClient(transport=transport)
    await client.aclose()


def test_canon_client_has_no_async_http_transport_injection():
    with pytest.raises(TypeError):
        HttpClient(base_url="http://example.com", transport=httpx.AsyncHTTPTransport())
