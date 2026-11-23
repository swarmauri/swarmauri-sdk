import asyncio

import httpx
import pytest

from swarmauri_canon_http import HttpClient
from swarmauri_canon_http.exceptions import HttpClientError


def test_httpx_client_exposes_http1_and_http2_toggles():
    client = httpx.Client(http1=True, http2=True, verify=False)
    client.close()

    assert isinstance(client, httpx.Client)


def test_canon_client_rejects_httpx_ssl_keywords():
    with pytest.raises(TypeError):
        HttpClient(base_url="https://example.com", verify=False)


def test_canon_client_rejects_unsupported_http3_version():
    client = HttpClient(base_url="https://example.com", version="3")

    with pytest.raises(HttpClientError):
        client.sync_request("GET", "/")


def test_httpx_does_not_initiate_websocket_handshake():
    def handle(request):
        assert "upgrade" not in request.headers
        assert "sec-websocket-key" not in request.headers
        return httpx.Response(200)

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        assert client.get("ws://example.com/socket").status_code == 200


@pytest.mark.asyncio
async def test_canon_async_request_support_exists(monkeypatch):
    async def dummy_open_connection(host, port, ssl=None):
        reader = asyncio.StreamReader()
        reader.feed_data(b"HTTP/1.1 200 OK\r\n\r\n")
        reader.feed_eof()

        class DummyWriter:
            def write(self, data):
                return None

            async def drain(self):
                return None

            def close(self):
                return None

            async def wait_closed(self):
                return None

        return reader, DummyWriter()

    monkeypatch.setattr(asyncio, "open_connection", dummy_open_connection)

    client = HttpClient(base_url="http://example.com")
    response = await client.aget("/async")

    assert "200 OK" in response
