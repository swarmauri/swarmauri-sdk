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


def test_query_param_encoding_matches_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    params = {"q": "hello world", "page": 2}
    client.get("/search", params=params)

    expected = httpx.Request("GET", "http://example.com/search", params=params)
    sent = RecordingConnection.last_request

    assert sent["path"] == expected.url.raw_path.decode("utf-8")


def test_base_url_join_behavior_matches_httpx_for_relative_paths(monkeypatch):
    patch_http_connections(monkeypatch)

    canon_client = HttpClient(base_url="http://example.com/api/")
    canon_client.get("v1/items")

    expected = httpx.Client(base_url="http://example.com/api/").build_request(
        "GET", "v1/items"
    )
    sent = RecordingConnection.last_request

    assert sent["path"] == expected.url.raw_path.decode("utf-8")
