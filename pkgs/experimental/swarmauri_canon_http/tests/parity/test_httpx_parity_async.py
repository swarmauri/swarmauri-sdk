import asyncio

import pytest

from swarmauri_canon_http import HttpClient


class AsyncCapture:
    request_bytes = b""


@pytest.mark.asyncio
async def test_async_get_writes_expected_request_line(monkeypatch):
    async def dummy_open_connection(host, port, ssl=None):
        reader = asyncio.StreamReader()
        reader.feed_data(b"HTTP/1.1 200 OK\r\n\r\n")
        reader.feed_eof()

        class DummyWriter:
            def write(self, data):
                AsyncCapture.request_bytes += data

            async def drain(self):
                return None

            def close(self):
                return None

            async def wait_closed(self):
                return None

        return reader, DummyWriter()

    monkeypatch.setattr(asyncio, "open_connection", dummy_open_connection)
    client = HttpClient(base_url="http://example.com")

    await client.aget("/async", params={"q": "value"})

    request_text = AsyncCapture.request_bytes.decode("utf-8")
    assert request_text.startswith("GET /async?q=value HTTP/1.1")
    assert "Host: example.com" in request_text


@pytest.mark.asyncio
async def test_async_post_json_writes_content_type_and_payload(monkeypatch):
    AsyncCapture.request_bytes = b""

    async def dummy_open_connection(host, port, ssl=None):
        reader = asyncio.StreamReader()
        reader.feed_data(b"HTTP/1.1 201 Created\r\n\r\n")
        reader.feed_eof()

        class DummyWriter:
            def write(self, data):
                AsyncCapture.request_bytes += data

            async def drain(self):
                return None

            def close(self):
                return None

            async def wait_closed(self):
                return None

        return reader, DummyWriter()

    monkeypatch.setattr(asyncio, "open_connection", dummy_open_connection)
    client = HttpClient(base_url="http://example.com")

    await client.apost("/async-json", json_data={"ok": True})

    request_text = AsyncCapture.request_bytes.decode("utf-8")
    assert "POST /async-json HTTP/1.1" in request_text
    assert "Content-Type: application/json" in request_text
    assert '{"ok": true}' in request_text
