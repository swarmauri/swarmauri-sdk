import http.client
import json

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


def test_json_body_serialization_parity_with_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    payload = {"enabled": True, "count": 4}
    client.post("/json", json_data=payload)

    expected = httpx.Request("POST", "http://example.com/json", json=payload)
    sent = RecordingConnection.last_request

    assert json.loads(sent["body"]) == json.loads(expected.content.decode("utf-8"))


def test_raw_content_body_parity_with_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    raw_body = "plain text body"
    client.post("/content", data=raw_body)

    expected = httpx.Request("POST", "http://example.com/content", content=raw_body)
    sent = RecordingConnection.last_request

    assert sent["body"] == expected.content.decode("utf-8")
