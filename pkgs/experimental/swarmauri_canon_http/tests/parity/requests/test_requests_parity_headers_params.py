from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import RecordingConnection, patch_http_connections
from tests.parity.requests.helpers import build_prepared_request


def test_headers_parity_with_requests(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    headers = {"Accept": "application/json", "X-Trace-Id": "trace-123"}
    client.get("/headers", headers=headers)

    expected = build_prepared_request(
        "GET", "http://example.com/headers", headers=headers
    )
    sent = RecordingConnection.last_request

    assert sent["headers"]["Accept"] == expected.headers["Accept"]
    assert sent["headers"]["X-Trace-Id"] == expected.headers["X-Trace-Id"]


def test_query_param_parity_with_requests(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    params = {"q": "hello world", "page": 2}
    client.get("/search", params=params)

    expected = build_prepared_request("GET", "http://example.com/search", params=params)
    sent = RecordingConnection.last_request

    assert sent["path"] == expected.path_url
