"""Exercise transport behavior without any provider credentials or API calls."""

import asyncio
from pathlib import Path
from typing import ClassVar

import httpx
import pytest
from pydantic import SecretStr

from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase

pytestmark = pytest.mark.unit


class OfflineTTS(HttpTTSMixin, TTSBase):
    _speech_url: ClassVar[str] = "https://speech.example.test/audio"
    api_key: SecretStr = SecretStr("offline-key")
    timeout: float = 5

    def _speech_payload(self, text, streaming):
        return {"text": text}


@pytest.fixture
def clients(monkeypatch):
    real_sync, real_async = httpx.Client, httpx.AsyncClient

    def install(handler):
        transport = httpx.MockTransport(handler)
        monkeypatch.setattr(
            httpx, "Client", lambda **kw: real_sync(transport=transport, **kw)
        )
        monkeypatch.setattr(
            httpx,
            "AsyncClient",
            lambda **kw: real_async(transport=transport, **kw),
        )

    return install


@pytest.mark.parametrize("status", [401, 429, 500])
def test_error_preserves_existing_file_and_is_not_retried(
    clients, tmp_path, status
):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(status)

    clients(respond)
    path = tmp_path / "existing.mp3"
    path.write_bytes(b"original")
    with pytest.raises(httpx.HTTPStatusError):
        OfflineTTS().predict("hello", str(path))
    assert path.read_bytes() == b"original"
    assert len(requests) == 1


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, content=b""),
        httpx.Response(200, json={"error": "not audio"}),
        httpx.Response(200, text="not audio"),
    ],
)
def test_invalid_audio_does_not_create_file(clients, tmp_path, response):
    clients(lambda request: response)
    path = tmp_path / "speech.mp3"
    with pytest.raises(ValueError):
        OfflineTTS().predict("hello", str(path))
    assert not path.exists()


class IncrementalAudio(httpx.SyncByteStream, httpx.AsyncByteStream):
    def __init__(self):
        self.read_count = 0
        self.closed = False

    def __iter__(self):
        for chunk in [b"first", b"second"]:
            assert not self.closed
            self.read_count += 1
            yield chunk

    async def __aiter__(self):
        for chunk in self:
            yield chunk

    def close(self):
        self.closed = True

    async def aclose(self):
        self.close()


def test_stream_delivers_incrementally_and_closes_on_cancel(clients):
    audio = IncrementalAudio()
    clients(lambda request: httpx.Response(200, stream=audio))
    stream = OfflineTTS().stream("hello")
    assert next(stream) == b"first"
    assert audio.read_count == 1
    assert not audio.closed
    stream.close()
    assert audio.closed


@pytest.mark.asyncio
async def test_async_stream_delivers_incrementally_and_closes_on_cancel(
    clients,
):
    audio = IncrementalAudio()
    clients(lambda request: httpx.Response(200, stream=audio))
    stream = OfflineTTS().astream("hello")
    assert await anext(stream) == b"first"
    assert audio.read_count == 1
    assert not audio.closed
    await stream.aclose()
    assert audio.closed


@pytest.mark.parametrize("text", ["", "  ", None])
def test_empty_input_never_sends_a_request(clients, text, tmp_path):
    clients(lambda request: pytest.fail("Unexpected HTTP request"))
    with pytest.raises(ValueError, match="non-empty"):
        OfflineTTS().predict(text, str(tmp_path / "speech.mp3"))


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1, True, 1.5, "2"])
async def test_invalid_concurrency_never_sends_a_request(clients, limit):
    clients(lambda request: pytest.fail("Unexpected HTTP request"))
    with pytest.raises(ValueError, match="positive integer"):
        await OfflineTTS().abatch({}, max_concurrent=limit)


@pytest.mark.asyncio
async def test_async_batch_bounds_concurrency_and_preserves_order(
    clients, tmp_path
):
    active, maximum = 0, 0

    async def respond(request):
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        await asyncio.sleep(0.01)
        active -= 1
        return httpx.Response(200, content=b"audio")

    clients(respond)
    outputs = {f"text {i}": str(tmp_path / f"{i}.mp3") for i in range(6)}
    paths = await OfflineTTS().abatch(outputs, max_concurrent=2)
    assert paths == list(outputs.values())
    assert maximum == 2
    assert all(Path(path).read_bytes() == b"audio" for path in paths)
