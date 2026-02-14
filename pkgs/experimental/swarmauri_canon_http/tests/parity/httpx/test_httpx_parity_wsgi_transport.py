import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def test_httpx_wsgi_transport_exists_and_is_constructible():
    def app(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"ok"]

    transport = httpx.WSGITransport(app=app)
    request = build_httpx_request("GET", "http://test")
    assert isinstance(transport, httpx.WSGITransport)
    assert request.url.host == "test"


def test_httpx_client_can_use_wsgi_transport_without_network():
    def app(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"ok"]

    client = httpx.Client(
        transport=httpx.WSGITransport(app=app), base_url="http://test"
    )
    response = client.get("/")
    client.close()

    assert response.status_code == 200
    assert response.text == "ok"


def test_canon_client_has_no_wsgi_transport_constructor_parity():
    def app(environ, start_response):
        start_response("200 OK", [])
        return [b""]

    with pytest.raises(TypeError):
        HttpClient(
            base_url="http://example.com", transport=httpx.WSGITransport(app=app)
        )
