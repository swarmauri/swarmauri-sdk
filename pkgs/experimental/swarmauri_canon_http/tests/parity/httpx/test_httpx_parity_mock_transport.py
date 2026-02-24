import httpx

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import RecordingConnection, patch_http_connections


def test_httpx_mock_transport_handles_request_without_network():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(204, request=request)
    )
    client = httpx.Client(transport=transport)
    response = client.get("http://example.com/no-network")
    client.close()

    assert response.status_code == 204


def test_canon_monkeypatched_transport_mocks_requests(monkeypatch):
    patch_http_connections(monkeypatch)

    client = HttpClient(base_url="http://example.com")
    client.get("/no-network")

    assert RecordingConnection.request_count == 1
