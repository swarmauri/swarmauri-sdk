import http.client
from dataclasses import dataclass

import httpx


@dataclass
class DummyResponse:
    status: int = 200
    headers: list[tuple[str, str]] | None = None
    body: bytes = b"{}"

    def getheaders(self):
        return self.headers or [("Content-Type", "application/json")]

    def read(self):
        return self.body


class RecordingConnection:
    last_request = None
    request_count = 0

    def __init__(self, netloc, timeout=None):
        self.netloc = netloc
        self.timeout = timeout

    def request(self, method, path, body=None, headers=None):
        RecordingConnection.request_count += 1
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
    RecordingConnection.last_request = None
    RecordingConnection.request_count = 0
    monkeypatch.setattr(http.client, "HTTPConnection", RecordingConnection)
    monkeypatch.setattr(http.client, "HTTPSConnection", RecordingHTTPSConnection)


def build_httpx_request(method, url, **kwargs):
    return httpx.Request(method, url, **kwargs)
