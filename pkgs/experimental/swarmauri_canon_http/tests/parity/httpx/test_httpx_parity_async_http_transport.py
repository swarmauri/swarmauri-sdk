import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def test_httpx_async_http_transport_exists_and_is_constructible():
    transport = httpx.AsyncHTTPTransport()
    request = build_httpx_request("GET", "https://example.com")

    assert isinstance(transport, httpx.AsyncHTTPTransport)
    assert request.url.scheme == "https"


@pytest.mark.asyncio
async def test_httpx_async_client_accepts_custom_async_transport():
    transport = httpx.AsyncHTTPTransport()
    client = httpx.AsyncClient(transport=transport)
    await client.aclose()


def test_canon_client_has_no_async_http_transport_injection():
    with pytest.raises(TypeError):
        HttpClient(base_url="http://example.com", transport=httpx.AsyncHTTPTransport())
