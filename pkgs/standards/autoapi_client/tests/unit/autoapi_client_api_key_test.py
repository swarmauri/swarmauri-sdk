import httpx
import pytest
from unittest.mock import patch

from autoapi_client import AutoAPIClient


@pytest.mark.unit
def test_api_key_included_in_rest_request():
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com", api_key="secret")
        client.get("/resource")

    assert captured["headers"]["x-api-key"] == "secret"


@pytest.mark.unit
def test_api_key_included_in_rpc_call():
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": None}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/rpc", api_key="topsecret")
        client.call("ping")

    assert captured["headers"]["x-api-key"] == "topsecret"


@pytest.mark.unit
def test_api_key_header_updates_and_removes():
    captured = []

    def fake_get(self, url, *, params=None, headers=None):
        captured.append(headers.copy() if headers else {})
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com", api_key="initial")
        client.get("/resource")
        client.api_key = "new-key"
        client.get("/resource")
        client.api_key = None
        client.get("/resource")

    assert captured[0]["x-api-key"] == "initial"
    assert captured[1]["x-api-key"] == "new-key"
    assert "x-api-key" not in captured[2]
