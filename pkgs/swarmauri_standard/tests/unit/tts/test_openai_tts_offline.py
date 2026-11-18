import importlib
import json
from pathlib import Path

import httpx
import pytest

from swarmauri_standard.tts.OpenaiTTS import OpenaiTTS

pytestmark = pytest.mark.unit
module = importlib.import_module("swarmauri_standard.tts.OpenaiTTS")


@pytest.fixture
def provider(monkeypatch):
    sync_client, async_client = httpx.Client, httpx.AsyncClient

    def handler(request):
        assert str(request.url) == "https://api.openai.com/v1/audio/speech"
        assert request.headers["authorization"] == "Bearer new-key"
        assert json.loads(request.content) == {
            "model": "gpt-4o-mini-tts",
            "voice": "alloy",
            "input": "hello",
        }
        return httpx.Response(200, content=b"audio")

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kw: sync_client(transport=transport, **kw),
    )
    monkeypatch.setattr(
        module.httpx,
        "AsyncClient",
        lambda **kw: async_client(transport=transport, **kw),
    )
    return OpenaiTTS(api_key="new-key", name="gpt-4o-mini-tts", voice="alloy")


def test_file_stream_and_batch(provider, tmp_path):
    output = tmp_path / "speech.mp3"
    assert provider.predict("hello", str(output)) == str(output.resolve())
    assert output.read_bytes() == b"audio"
    assert b"".join(provider.stream("hello")) == b"audio"
    assert provider.batch({"hello": str(output)}) == [str(output.resolve())]
    assert provider.get_allowed_models() == provider.allowed_models


@pytest.mark.asyncio
async def test_async_file_stream_and_batch(provider, tmp_path):
    output = tmp_path / "speech.mp3"
    assert await provider.apredict("hello", str(output)) == str(
        output.resolve()
    )
    assert output.read_bytes() == b"audio"
    assert (
        b"".join([chunk async for chunk in provider.astream("hello")])
        == b"audio"
    )
    assert await provider.abatch({"hello": str(output)}) == [
        str(output.resolve())
    ]


def test_agent_uses_replacement(provider, tmp_path):
    from swarmauri_agent_texttospeech import TextToSpeechAgent

    output = tmp_path / "agent.mp3"
    agent = TextToSpeechAgent(tts=provider, output_path=str(output))
    assert Path(agent.exec("hello")).read_bytes() == b"audio"


@pytest.mark.parametrize("method", ["predict", "stream"])
def test_provider_errors_surface(monkeypatch, method, tmp_path):
    real_client = httpx.Client
    transport = httpx.MockTransport(lambda request: httpx.Response(401))
    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kw: real_client(transport=transport, **kw),
    )
    provider = OpenaiTTS(api_key="bad-key")
    with pytest.raises((httpx.HTTPStatusError, RuntimeError)):
        if method == "stream":
            list(provider.stream("hello"))
        else:
            provider.predict("hello", str(tmp_path / "failed.mp3"))
    assert not (tmp_path / "failed.mp3").exists()


class IncrementalAudio(httpx.SyncByteStream, httpx.AsyncByteStream):
    def __init__(self):
        self.chunks_read = 0
        self.closed = False

    def __iter__(self):
        for chunk in [b"first", b"second"]:
            assert not self.closed
            self.chunks_read += 1
            yield chunk

    async def __aiter__(self):
        for chunk in self:
            yield chunk

    def close(self):
        self.closed = True

    async def aclose(self):
        self.close()


def test_stream_is_incremental_and_closes_on_cancel(monkeypatch):
    audio = IncrementalAudio()
    real_client = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, stream=audio)
    )
    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kw: real_client(transport=transport, **kw),
    )
    chunks = OpenaiTTS(api_key="key").stream("hello")
    assert next(chunks) == b"first"
    assert audio.chunks_read == 1
    assert not audio.closed
    chunks.close()
    assert audio.closed


@pytest.mark.asyncio
async def test_async_stream_is_incremental_and_closes_on_cancel(monkeypatch):
    audio = IncrementalAudio()
    real_client = httpx.AsyncClient
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, stream=audio)
    )
    monkeypatch.setattr(
        module.httpx,
        "AsyncClient",
        lambda **kw: real_client(transport=transport, **kw),
    )
    chunks = OpenaiTTS(api_key="key").astream("hello")
    assert await anext(chunks) == b"first"
    assert audio.chunks_read == 1
    assert not audio.closed
    await chunks.aclose()
    assert audio.closed
