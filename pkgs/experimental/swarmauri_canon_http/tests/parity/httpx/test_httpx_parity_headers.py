from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import (
    RecordingConnection,
    build_httpx_request,
    patch_http_connections,
)


def test_custom_headers_parity_with_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    headers = {"Accept": "application/json", "X-Trace-Id": "trace-123"}
    client.get("/headers", headers=headers)

    expected = build_httpx_request("GET", "http://example.com/headers", headers=headers)
    sent = RecordingConnection.last_request

    assert sent["headers"]["Accept"] == expected.headers["Accept"]
    assert sent["headers"]["X-Trace-Id"] == expected.headers["X-Trace-Id"]


def test_json_content_type_header_matches_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    payload = {"name": "swarmauri", "kind": "canon-http"}
    client.post("/json", json_data=payload)

    expected = build_httpx_request("POST", "http://example.com/json", json=payload)
    sent = RecordingConnection.last_request

    assert sent["headers"]["Content-Type"] == expected.headers["Content-Type"]
