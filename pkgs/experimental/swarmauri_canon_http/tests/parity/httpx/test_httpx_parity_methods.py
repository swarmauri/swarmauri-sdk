import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import (
    RecordingConnection,
    build_httpx_request,
    patch_http_connections,
)


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
        expected = build_httpx_request(
            http_method, "http://example.com/resource", content="payload"
        )
    else:
        getattr(client, method_name)("/resource")
        expected = build_httpx_request(http_method, "http://example.com/resource")

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
