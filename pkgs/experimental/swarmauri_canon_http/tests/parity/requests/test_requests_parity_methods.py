import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import RecordingConnection, patch_http_connections
from tests.parity.requests.helpers import build_prepared_request


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
def test_sync_method_parity_with_requests_prepared_request(
    monkeypatch, method_name, http_method
):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    if method_name in {"post", "put", "patch", "delete"}:
        getattr(client, method_name)("/resource", data="payload")
        expected = build_prepared_request(
            http_method, "http://example.com/resource", data="payload"
        )
    else:
        getattr(client, method_name)("/resource")
        expected = build_prepared_request(http_method, "http://example.com/resource")

    sent = RecordingConnection.last_request
    assert sent["method"] == expected.method
    assert sent["path"] == expected.path_url
