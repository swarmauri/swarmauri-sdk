import pytest

import httpx

from swarmauri_canon_http import HttpClient


def test_httpx_asgi_transport_exists_and_is_constructible():
    transport = httpx.ASGITransport(app=lambda scope: None)
    assert isinstance(transport, httpx.ASGITransport)


def test_canon_client_has_no_asgi_transport_constructor_parity():
    with pytest.raises(TypeError):
        HttpClient(
            base_url="http://example.com",
            transport=httpx.ASGITransport(app=lambda s: None),
        )
