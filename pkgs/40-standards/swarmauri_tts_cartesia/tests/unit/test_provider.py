"""Offline package and documented request-contract tests."""

import importlib
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_cartesia import CartesiaTTS, __version__
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
    assert __version__ == version("swarmauri_tts_cartesia")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_cartesia")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p
        for p in entry_points(group="swarmauri.tts")
        if p.name == "CartesiaTTS"
    )
    assert point.load() is CartesiaTTS
    assert issubclass(CartesiaTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = CartesiaTTS(api_key="offline-key", voice="voice-id")
    path = tmp_path / "speech.mp3"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"audio"
    assert len(transport) == 1
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = CartesiaTTS(api_key="offline-key", voice="voice-id")
    path = str(tmp_path / "speech.mp3")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_cartesia")
    assert module.CartesiaTTS is CartesiaTTS


@pytest.mark.parametrize(
    "settings",
    [
        {"name": "not-a-model"},
        {"timeout": 0},
        {"base_url": "https://other.example"},
        {"speed": 2},
        {"sample_rate": 123},
        {"voice": ""},
        {"api_version": "invalid"},
        {"response_format": "json"},
    ],
)
def test_invalid_settings_fail_before_requests(transport, settings):
    with pytest.raises(ValueError):
        CartesiaTTS(
            **({"api_key": "offline-key", "voice": "voice-id"} | settings)
        )
    assert transport == []


def test_documented_contract(transport, tmp_path):
    import json

    provider = CartesiaTTS(
        api_key="offline-key",
        voice="voice-id",
        response_format="wav",
        speed=0.8,
        language="en",
    )
    provider.predict("hello", str(tmp_path / "out.wav"))
    request = transport[0]
    assert str(request.url) == "https://api.cartesia.ai/tts/bytes"
    assert request.headers["authorization"] == "Bearer offline-key"
    assert request.headers["cartesia-version"] == "2026-08-14"
    assert json.loads(request.content) == {
        "model_id": "sonic-3.6",
        "transcript": "hello",
        "voice": "voice-id",
        "output_format": {
            "container": "wav",
            "sample_rate": 44100,
            "encoding": "pcm_s16le",
        },
        "generation_config": {"speed": 0.8},
        "language": "en",
    }
    mp3 = CartesiaTTS(api_key="offline-key", voice="voice-id")._payload(
        "hello", False
    )
    assert mp3["output_format"] == {
        "container": "mp3",
        "sample_rate": 44100,
        "bit_rate": 128000,
    }
