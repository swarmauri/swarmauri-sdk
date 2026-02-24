import httpx

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import RecordingConnection, patch_http_connections


def test_httpx_http_transport_exists_and_is_constructible():
    transport = httpx.HTTPTransport()
    assert isinstance(transport, httpx.HTTPTransport)


def test_canon_sync_requests_use_builtin_http_client_transport(monkeypatch):
    patch_http_connections(monkeypatch)

    client = HttpClient(base_url="http://example.com")
    client.get("/transport")

    assert RecordingConnection.request_count == 1
