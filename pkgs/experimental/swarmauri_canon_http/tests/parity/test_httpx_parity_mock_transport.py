import http.client

import httpx

from swarmauri_canon_http import HttpClient


class DummyResponse:
    def __init__(self, status=200, headers=None, body=b"mock"):
        self.status = status
        self._headers = headers or []
        self._body = body

    def getheaders(self):
        return self._headers

    def read(self):
        return self._body


class RecordingConnection:
    calls = 0

    def __init__(self, netloc, timeout=None):
        self.netloc = netloc
        self.timeout = timeout

    def request(self, method, path, body=None, headers=None):
        RecordingConnection.calls += 1

    def getresponse(self):
        return DummyResponse()

    def close(self):
        return None


def test_httpx_mock_transport_handles_request_without_network():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(204, request=request)
    )
    client = httpx.Client(transport=transport)
    response = client.get("http://example.com/no-network")
    client.close()

    assert response.status_code == 204


def test_canon_monkeypatched_transport_mocks_requests(monkeypatch):
    monkeypatch.setattr(http.client, "HTTPConnection", RecordingConnection)

    client = HttpClient(base_url="http://example.com")
    client.get("/no-network")

    assert RecordingConnection.calls == 1
