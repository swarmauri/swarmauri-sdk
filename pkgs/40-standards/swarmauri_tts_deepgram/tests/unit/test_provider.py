"""Offline package and documented request-contract tests."""

import importlib
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_deepgram import DeepgramTTS, __version__
from swarmauri_base.tts.TTSBase import TTSBase

pytestmark = pytest.mark.unit


@pytest.fixture
def transport(monkeypatch):
    real_sync, real_async = httpx.Client, httpx.AsyncClient
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200, content=b"audio", headers={"content-type": "audio/mpeg"}
        )

    mock = httpx.MockTransport(handler)
    monkeypatch.setattr(
        httpx, "Client", lambda **kw: real_sync(transport=mock, **kw)
    )
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: real_async(transport=mock, **kw)
    )
    return requests


def test_alpha_metadata_entrypoint_and_independent_dependencies():
    assert __version__ == version("swarmauri_tts_deepgram")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_deepgram")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p
        for p in entry_points(group="swarmauri.tts")
        if p.name == "DeepgramTTS"
    )
    assert point.load() is DeepgramTTS
    assert issubclass(DeepgramTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = DeepgramTTS(api_key="offline-key")
    path = tmp_path / "speech.mp3"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"audio"
    assert len(transport) == 1
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = DeepgramTTS(api_key="offline-key")
    path = str(tmp_path / "speech.mp3")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_deepgram")
    assert module.DeepgramTTS is DeepgramTTS


@pytest.mark.parametrize(
    "settings",
    [
        {"name": "not-a-model"},
        {"timeout": 0},
        {"base_url": "https://other.example"},
        {"encoding": "json"},
        {"sample_rate": 24000},
        {"container": "wav"},
        {"encoding": "mulaw", "sample_rate": 24000},
    ],
)
def test_invalid_settings_fail_before_requests(transport, settings):
    with pytest.raises(ValueError):
        DeepgramTTS(**({"api_key": "offline-key"} | settings))
    assert transport == []


def test_documented_contract(transport, tmp_path):
    import json

    provider = DeepgramTTS(
        api_key="offline-key", encoding="linear16", sample_rate=24000
    )
    provider.predict("hello", str(tmp_path / "out.wav"))
    request = transport[0]
    assert request.url.host == "api.deepgram.com"
    assert request.url.path == "/v1/speak"
    assert dict(request.url.params) == {
        "model": "aura-2-thalia-en",
        "encoding": "linear16",
        "sample_rate": "24000",
        "container": "wav",
    }
    assert request.headers["authorization"] == "Token offline-key"
    assert json.loads(request.content) == {"text": "hello"}
    default = httpx.URL(
        DeepgramTTS(api_key="offline-key")._speech_endpoint(False)
    )
    assert dict(default.params) == {
        "model": "aura-2-thalia-en",
        "encoding": "mp3",
    }
    raw = DeepgramTTS(
        api_key="offline-key",
        encoding="mulaw",
        container="none",
        sample_rate=8000,
    )
    assert httpx.URL(raw._speech_endpoint(True)).params["container"] == "none"
