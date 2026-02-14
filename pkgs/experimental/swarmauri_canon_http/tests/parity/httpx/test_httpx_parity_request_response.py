import httpx

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import (
    DummyResponse,
    RecordingConnection,
    patch_http_connections,
)


def test_httpx_request_object_exposes_rich_api():
    request = httpx.Request("POST", "https://example.com/api", json={"ok": True})

    assert request.method == "POST"
    assert request.url.path == "/api"
    assert request.read() == b'{"ok":true}'


def test_httpx_response_object_has_status_helpers_and_errors():
    response = httpx.Response(404, request=httpx.Request("GET", "https://example.com"))

    assert response.is_error is True


def test_canon_sync_request_returns_primitive_tuple(monkeypatch):
    patch_http_connections(monkeypatch)

    def _text_response(self):
        return DummyResponse(
            status=200, headers=[("Content-Type", "text/plain")], body=b"ok"
        )

    monkeypatch.setattr(RecordingConnection, "getresponse", _text_response)

    client = HttpClient(base_url="http://example.com")
    status, headers, body = client.get("/resource")

    assert status == 200
    assert isinstance(headers, list)
    assert body == b"ok"
