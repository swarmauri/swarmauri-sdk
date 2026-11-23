"""Offline package and documented request-contract tests."""

import base64
import importlib
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_gemini import GeminiTTS, __version__
from swarmauri_base.tts.TTSBase import TTSBase

pytestmark = pytest.mark.unit


@pytest.fixture
def transport(monkeypatch):
    real_sync, real_async = httpx.Client, httpx.AsyncClient
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "audio",
                                "data": base64.b64encode(
                                    b"RIFF0000WAVEaudio"
                                ).decode(),
                            }
                        ],
                    }
                ],
            },
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
    assert __version__ == version("swarmauri_tts_gemini")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_gemini")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p for p in entry_points(group="swarmauri.tts") if p.name == "GeminiTTS"
    )
    assert point.load() is GeminiTTS
    assert issubclass(GeminiTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = GeminiTTS(api_key="offline-key", voice="Kore")
    path = tmp_path / "speech.wav"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"RIFF0000WAVEaudio"
    assert len(transport) == 1
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = GeminiTTS(api_key="offline-key", voice="Kore")
    path = str(tmp_path / "speech.wav")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_gemini")
    assert module.GeminiTTS is GeminiTTS


@pytest.mark.parametrize(
    "settings",
    [
        {"name": "not-a-model"},
        {"timeout": 0},
        {"base_url": "https://other.example"},
        {"name": "gemini-2.5-flash-preview-tts"},
        {"voice": ""},
        {"style": ""},
    ],
)
def test_invalid_settings_fail_before_requests(transport, settings):
    with pytest.raises(ValueError):
        GeminiTTS(**({"api_key": "offline-key", "voice": "Kore"} | settings))
    assert transport == []


def test_documented_contract(transport, tmp_path):
    import json

    provider = GeminiTTS(api_key="offline-key", style="cheerful")
    provider.predict("hello", str(tmp_path / "out.wav"))
    request = transport[0]
    assert (
        str(request.url)
        == "https://generativelanguage.googleapis.com/v1beta/interactions"
    )
    assert request.headers["x-goog-api-key"] == "offline-key"
    assert "authorization" not in request.headers
    assert json.loads(request.content) == {
        "model": "gemini-3.8-flash-tts",
        "input": [
            {
                "type": "user_input",
                "content": [
                    {
                        "type": "text",
                        "text": "hello",
                        "annotations": [
                            {"type": "speech_metadata", "style": "cheerful"}
                        ],
                    }
                ],
            }
        ],
        "response_format": {
            "type": "audio",
            "mime_type": "audio/wav",
            "sample_rate": 24000,
        },
        "generation_config": {"speech_config": [{"voice": "Kore"}]},
        "stream": False,
        "store": False,
    }


@pytest.mark.parametrize(
    "data",
    [
        None,
        {},
        {"status": "failed"},
        {"status": "completed", "steps": None},
        {
            "status": "completed",
            "steps": [{"type": "model_output", "content": None}],
        },
        {
            "status": "completed",
            "steps": [
                {
                    "type": "model_output",
                    "content": [{"type": "audio", "data": "%%%"}],
                }
            ],
        },
        {
            "status": "completed",
            "steps": [
                {
                    "type": "model_output",
                    "content": [{"type": "audio", "data": "YQ=="}],
                }
            ],
        },
    ],
)
def test_invalid_response_preserves_file(monkeypatch, tmp_path, data):
    real = httpx.Client

    def handler(request):
        return httpx.Response(
            200,
            content=__import__("json").dumps(data),
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: real(transport=httpx.MockTransport(handler), **kw),
    )
    path = tmp_path / "speech.wav"
    path.write_bytes(b"existing")
    with pytest.raises((ValueError, RuntimeError)):
        GeminiTTS(api_key="offline-key").predict("hello", str(path))
    assert path.read_bytes() == b"existing"


def test_only_model_output_audio_is_selected():
    provider = GeminiTTS(api_key="offline-key")
    audio = base64.b64encode(b"RIFF0000WAVEfinal").decode()
    response = httpx.Response(
        200,
        json={
            "status": "completed",
            "steps": [
                {
                    "type": "user_input",
                    "content": [{"type": "audio", "data": "ignored"}],
                },
                {
                    "type": "model_output",
                    "content": [{"type": "audio", "data": audio}],
                },
            ],
        },
    )
    assert provider._audio_content(response) == b"RIFF0000WAVEfinal"
