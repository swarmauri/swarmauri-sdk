import httpx

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import RecordingConnection, patch_http_connections


def test_httpx_request_dispatches_any_http_verb():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(202))
    )
    response = client.request("TRACE", "https://example.com")
    client.close()

    assert response.status_code == 202


def test_httpx_has_streaming_interface():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )

    with client.stream("GET", "https://example.com") as response:
        assert response.status_code == 200

    client.close()


def test_canon_uses_verb_helpers_but_has_no_stream_method(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    client.get("/")

    assert RecordingConnection.request_count == 1
    assert not hasattr(client, "stream")
    assert not hasattr(client, "request")


def test_canon_exposes_sync_request_primitive_for_generic_verb(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    client.sync_request("TRACE", "/trace")

    assert RecordingConnection.request_count >= 1


def test_canon_has_no_shortcut_for_connect_method():
    client = HttpClient(base_url="http://example.com")

    assert not hasattr(client, "connect")
    assert not hasattr(client, "aconnect")
