import pytest

from peagen.gateway import _client_ip


class DummyClient:
    def __init__(self, host: str):
        self.host = host


class DummyRequest:
    def __init__(self, headers: dict[str, str], host: str = "192.168.0.1"):
        self.headers = headers
        self.client = DummyClient(host)


@pytest.mark.unit
def test_get_client_ip_forwarded():
    req = DummyRequest({"x-forwarded-for": "203.0.113.7, 10.0.0.1"})
    assert _client_ip(req) == "203.0.113.7"


@pytest.mark.unit
def test_get_client_ip_fallback():
    req = DummyRequest({}, "10.1.1.1")
    assert _client_ip(req) == "10.1.1.1"
