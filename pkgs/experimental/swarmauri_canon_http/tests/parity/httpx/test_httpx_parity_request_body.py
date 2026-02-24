import json

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import (
    RecordingConnection,
    build_httpx_request,
    patch_http_connections,
)


def test_json_body_serialization_parity_with_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    payload = {"enabled": True, "count": 4}
    client.post("/json", json_data=payload)

    expected = build_httpx_request("POST", "http://example.com/json", json=payload)
    sent = RecordingConnection.last_request

    assert json.loads(sent["body"]) == json.loads(expected.content.decode("utf-8"))


def test_raw_content_body_parity_with_httpx(monkeypatch):
    patch_http_connections(monkeypatch)
    client = HttpClient(base_url="http://example.com")

    raw_body = "plain text body"
    client.post("/content", data=raw_body)

    expected = build_httpx_request(
        "POST", "http://example.com/content", content=raw_body
    )
    sent = RecordingConnection.last_request

    assert sent["body"] == expected.content.decode("utf-8")
