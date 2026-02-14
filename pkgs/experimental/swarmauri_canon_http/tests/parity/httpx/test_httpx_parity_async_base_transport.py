import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def test_httpx_async_base_transport_is_available():
    request = build_httpx_request("GET", "http://example.com")

    assert hasattr(httpx, "AsyncBaseTransport")
    assert issubclass(httpx.AsyncBaseTransport, object)
    assert request.url.host == "example.com"


def test_canon_client_rejects_async_transport_keyword():
    with pytest.raises(TypeError):
        HttpClient(base_url="http://example.com", transport=httpx.AsyncBaseTransport())
