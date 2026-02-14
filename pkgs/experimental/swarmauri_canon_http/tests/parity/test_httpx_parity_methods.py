import http.client

import httpx
import pytest

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
            "netloc": self.netloc,
            "timeout": self.timeout,
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


@pytest.mark.parametrize(
    ("method_name", "http_method"),
    [
        ("get", "GET"),
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
        ("delete", "DELETE"),
        ("head", "HEAD"),
        ("options", "OPTIONS"),
    ],
)
def test_sync_method_parity_with_httpx(monkeypatch, method_name, http_method):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    if method_name in {"post", "put", "patch", "delete"}:
        getattr(client, method_name)("/resource", data="payload")
        expected = httpx.Request(
            http_method, "http://example.com/resource", content="payload"
        )
    else:
        getattr(client, method_name)("/resource")
        expected = httpx.Request(http_method, "http://example.com/resource")

    sent = RecordingConnection.last_request
    assert sent["method"] == expected.method
    assert sent["path"] == expected.url.raw_path.decode("utf-8")


def test_sync_get_uses_timeout_like_httpx_client(monkeypatch):
    patch_http_connections(monkeypatch)
    timeout_value = 3.0
    client = HttpClient(base_url="http://example.com", timeout=timeout_value)

    client.get("/timeout")

    sent = RecordingConnection.last_request
    assert sent["timeout"] == timeout_value
