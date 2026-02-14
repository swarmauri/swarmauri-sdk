import http.client

import httpx

from swarmauri_canon_http import HttpClient


class DummyResponse:
    def __init__(self, status=200, headers=None, body=b"{}"):
        self.status = status
        self._headers = headers or [("Content-Type", "application/json")]
        self._body = body

    def getheaders(self):
        return self._headers

    def read(self):
        return self._body


class RecordingConnection:
    last_request = None

    def __init__(self, netloc, timeout=None):
        self.netloc = netloc
        self.timeout = timeout

    def request(self, method, path, body=None, headers=None):
        RecordingConnection.last_request = {
            "method": method,
            "path": path,
            "body": body,
            "headers": headers or {},
        }

    def getresponse(self):
        return DummyResponse()

    def close(self):
        return None


class RecordingHTTPSConnection(RecordingConnection):
    pass


def patch_http_connections(monkeypatch):
    monkeypatch.setattr(http.client, "HTTPConnection", RecordingConnection)
    monkeypatch.setattr(http.client, "HTTPSConnection", RecordingHTTPSConnection)


def test_custom_headers_parity_with_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    headers = {"Accept": "application/json", "X-Trace-Id": "trace-123"}
    client.get("/headers", headers=headers)

    expected = httpx.Request("GET", "http://example.com/headers", headers=headers)
    sent = RecordingConnection.last_request

    assert sent["headers"]["Accept"] == expected.headers["Accept"]
    assert sent["headers"]["X-Trace-Id"] == expected.headers["X-Trace-Id"]


def test_json_content_type_header_matches_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    payload = {"name": "swarmauri", "kind": "canon-http"}
    client.post("/json", json_data=payload)

    expected = httpx.Request("POST", "http://example.com/json", json=payload)
    sent = RecordingConnection.last_request

    assert sent["headers"]["Content-Type"] == expected.headers["Content-Type"]
