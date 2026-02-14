import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def test_httpx_asgi_transport_exists_and_is_constructible():
    transport = httpx.ASGITransport(app=lambda scope: None)
    request = build_httpx_request("GET", "http://example.com")

    assert isinstance(transport, httpx.ASGITransport)
    assert request.method == "GET"


def test_canon_client_has_no_asgi_transport_constructor_parity():
    with pytest.raises(TypeError):
        HttpClient(
            base_url="http://example.com",
            transport=httpx.ASGITransport(app=lambda s: None),
        )
