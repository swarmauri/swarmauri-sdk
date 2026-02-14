import http.client

import httpx

from swarmauri_canon_http import HttpClient


class DummyResponse:
    def __init__(self, status=200, headers=None, body=b"ok"):
        self.status = status
        self._headers = headers or []
        self._body = body

    def getheaders(self):
        return self._headers

    def read(self):
        return self._body


class RecordingConnection:
    called = False

    def __init__(self, netloc, timeout=None):
        self.netloc = netloc
        self.timeout = timeout

    def request(self, method, path, body=None, headers=None):
        RecordingConnection.called = True

    def getresponse(self):
        return DummyResponse()

    def close(self):
        return None


class RecordingHTTPSConnection(RecordingConnection):
    pass


def test_httpx_http_transport_exists_and_is_constructible():
    transport = httpx.HTTPTransport()
    assert isinstance(transport, httpx.HTTPTransport)


def test_canon_sync_requests_use_builtin_http_client_transport(monkeypatch):
    monkeypatch.setattr(http.client, "HTTPConnection", RecordingConnection)
    monkeypatch.setattr(http.client, "HTTPSConnection", RecordingHTTPSConnection)

    client = HttpClient(base_url="http://example.com")
    client.get("/transport")

    assert RecordingConnection.called is True
