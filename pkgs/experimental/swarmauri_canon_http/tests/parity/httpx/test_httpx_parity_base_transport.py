import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def test_httpx_base_transport_is_available():
    request = build_httpx_request("GET", "http://example.com")

    assert hasattr(httpx, "BaseTransport")
    assert issubclass(httpx.BaseTransport, object)
    assert request.url.path == "/"


def test_httpx_client_accepts_base_transport_subclass():
    class DummyTransport(httpx.BaseTransport):
        def handle_request(self, request):
            return httpx.Response(200, request=request)

    transport = DummyTransport()
    client = httpx.Client(transport=transport)
    response = client.get("http://example.com")
    client.close()

    assert response.status_code == 200


def test_canon_client_rejects_base_transport_keyword():
    with pytest.raises(TypeError):
        HttpClient(base_url="http://example.com", transport=httpx.BaseTransport())
