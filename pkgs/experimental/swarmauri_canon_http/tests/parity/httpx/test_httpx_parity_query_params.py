import httpx

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import RecordingConnection, patch_http_connections


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
