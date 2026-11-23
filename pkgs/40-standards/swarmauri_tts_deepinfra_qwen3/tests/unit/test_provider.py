"""Offline package and documented request-contract tests."""

import base64
import importlib
import json
from pathlib import Path
import jsonschema
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_deepinfra_qwen3 import DeepInfraQwen3TTS, __version__
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
                "audio": "data:audio/wav;base64,"
                + base64.b64encode(b"RIFF0000WAVEaudio").decode(),
                "inference_status": {"status": "succeeded"},
                "output_format": "wav",
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
    assert __version__ == version("swarmauri_tts_deepinfra_qwen3")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_deepinfra_qwen3")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p
        for p in entry_points(group="swarmauri.tts")
        if p.name == "DeepInfraQwen3TTS"
    )
    assert point.load() is DeepInfraQwen3TTS
    assert issubclass(DeepInfraQwen3TTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = DeepInfraQwen3TTS(api_key="offline-key")
    path = tmp_path / "speech.wav"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"RIFF0000WAVEaudio"
    assert len(transport) == 1
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = DeepInfraQwen3TTS(api_key="offline-key")
    path = str(tmp_path / "speech.wav")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_deepinfra_qwen3")
    assert module.DeepInfraQwen3TTS is DeepInfraQwen3TTS


def test_native_payload_matches_published_schema(transport, tmp_path):
    provider = DeepInfraQwen3TTS(api_key="offline-key")
    provider.predict("hello", str(tmp_path / "speech.wav"))
    request = transport[0]
    fixture = json.loads(
        (Path(__file__).parents[1] / "fixtures/native-schema.json").read_text()
    )
    assert (
        str(request.url)
        == "https://api.deepinfra.com/v1/inference/" + fixture["model"]
    )
    assert request.headers["authorization"] == "Bearer offline-key"
    payload = json.loads(request.content)
    jsonschema.validate(payload, fixture["input"])
    assert "model" not in payload
    assert "webhook" not in payload
    if "Kokoro" in fixture["model"]:
        assert payload == {
            "text": "hello",
            "preset_voice": ["af_bella"],
            "output_format": "wav",
            "speed": 1.0,
            "stream": False,
        }
    else:
        assert payload["input"] == "hello"
        assert payload["response_format"] == "wav"
        assert payload["voice"] == "Vivian"
        assert "stream" not in payload


@pytest.mark.asyncio
async def test_streams_rejected_before_http(transport):
    provider = DeepInfraQwen3TTS(api_key="offline-key")
    with pytest.raises(NotImplementedError):
        list(provider.stream("hello"))
    with pytest.raises(NotImplementedError):
        await anext(provider.astream("hello"))
    assert not transport


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"audio": None},
        {"audio": ""},
        {"audio": "%%%"},
        {"audio": "https://example.test/voice.wav"},
        {"audio": "data:text/plain;base64,YQ=="},
        {"audio": "YQ=="},
        {"error": "failed"},
        {"audio": "YQ==", "inference_status": {"status": "failed"}},
        {"audio": "YQ==", "inference_status": None},
        {"audio": "YQ==", "output_format": "mp3"},
        {"audio": "YQ==", "output_format": []},
    ],
)
def test_invalid_json_audio_preserves_existing_file(
    monkeypatch, tmp_path, data
):
    real = httpx.Client
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=data)

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: real(transport=httpx.MockTransport(handler), **kw),
    )
    path = tmp_path / "speech.wav"
    path.write_bytes(b"existing")
    with pytest.raises((ValueError, RuntimeError)):
        DeepInfraQwen3TTS(api_key="offline-key").predict("hello", str(path))
    assert path.read_bytes() == b"existing"
    assert len(requests) == 1


@pytest.mark.parametrize("uri", [False, True])
def test_base64_pcm_has_no_added_header(uri):
    provider = DeepInfraQwen3TTS(api_key="offline-key", response_format="pcm")
    encoded = base64.b64encode(b"\x00\x00\x01\x00").decode()
    if uri:
        encoded = "data:audio/pcm;base64," + encoded
    assert (
        provider._audio_content(httpx.Response(200, json={"audio": encoded}))
        == b"\x00\x00\x01\x00"
    )


@pytest.mark.parametrize("text", ["", "  ", "x" * (4000 + 1)])
def test_invalid_text_is_local(transport, tmp_path, text):
    with pytest.raises(ValueError):
        DeepInfraQwen3TTS(api_key="offline-key").predict(
            text, str(tmp_path / "output.wav")
        )
    assert not transport


@pytest.mark.parametrize(
    "settings",
    [
        {"name": "not-a-model"},
        {"timeout": 0},
        {"base_url": "https://example.test"},
    ],
)
def test_bad_configuration(transport, settings):
    with pytest.raises(ValueError):
        DeepInfraQwen3TTS(**({"api_key": "offline-key"} | {} | settings))
    assert not transport


def test_preset_and_instruction_contract():
    provider = DeepInfraQwen3TTS(
        api_key="offline-key",
        voice="saved-voice-id",
        instruct="Warm and calm",
        language="English",
    )
    assert provider._payload("hello", False) == {
        "input": "hello",
        "voice": "saved-voice-id",
        "instruct": "Warm and calm",
        "language": "English",
        "response_format": "wav",
    }
    with pytest.raises(ValueError):
        DeepInfraQwen3TTS(api_key="offline-key", language="not-a-language")
