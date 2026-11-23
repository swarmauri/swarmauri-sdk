"""Offline package and documented request-contract tests."""

import importlib
import json
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_together import TogetherTTS, __version__
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
    assert __version__ == version("swarmauri_tts_together")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_together")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p
        for p in entry_points(group="swarmauri.tts")
        if p.name == "TogetherTTS"
    )
    assert point.load() is TogetherTTS
    assert issubclass(TogetherTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = TogetherTTS(api_key="offline-key")
    path = tmp_path / "speech.mp3"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"audio"
    assert str(transport[0].url) == "https://api.together.ai/v1/audio/speech"
    assert transport[0].headers["authorization"] == "Bearer offline-key"
    assert json.loads(transport[0].content) == {
        "model": "canopylabs/orpheus-3b-0.1-ft",
        "input": "hello",
        "voice": "tara",
        "response_format": "mp3",
        "sample_rate": 24000,
        "stream": False,
    }
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = TogetherTTS(api_key="offline-key")
    path = str(tmp_path / "speech.mp3")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_together")
    assert module.TogetherTTS is TogetherTTS


@pytest.mark.parametrize(
    "settings",
    [
        {"name": "not-a-model"},
        {"timeout": 0},
        {"response_format": "json"},
        {"base_url": "https://other.example"},
    ],
)
def test_invalid_settings_fail_before_requests(transport, settings):
    with pytest.raises(ValueError):
        TogetherTTS(api_key="offline-key", **settings)
    assert transport == []
