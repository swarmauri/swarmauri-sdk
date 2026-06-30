import httpx

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import (
    RecordingConnection,
    patch_http_connections,
)
from tests.parity.requests.helpers import build_prepared_request


def test_requests_prepared_request_exposes_request_metadata():
    prepared = build_prepared_request(
        "POST", "https://example.com/api", json={"ok": True}
    )

    assert prepared.method == "POST"
    assert prepared.url.path == "/api"
    assert prepared.content == b'{"ok":true}'


def test_requests_response_object_has_status_helpers():
    response = httpx.Response(404)

    assert response.is_success is False


def test_canon_sync_request_returns_primitive_tuple(monkeypatch):
    patch_http_connections(monkeypatch)

    client = HttpClient(base_url="http://example.com")
    status, headers, body = client.get("/resource")

    assert status == 200
    assert isinstance(headers, list)
    assert isinstance(body, bytes)
    assert RecordingConnection.last_request["path"] == "/resource"
