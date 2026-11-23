"""Offline package and documented request-contract tests."""

import base64
import importlib
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_gemini_dialogue import (
    GeminiDialogueTTS,
    GeminiDialogueTurn,
    __version__,
)
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
    assert __version__ == version("swarmauri_tts_gemini_dialogue")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_gemini_dialogue")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p
        for p in entry_points(group="swarmauri.tts")
        if p.name == "GeminiDialogueTTS"
    )
    assert point.load() is GeminiDialogueTTS
    assert issubclass(GeminiDialogueTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = GeminiDialogueTTS(
        api_key="offline-key",
        speaker_voices={"One": "Puck", "Two": "Kore"},
        default_speaker="One",
    )
    path = tmp_path / "speech.wav"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"RIFF0000WAVEaudio"
    assert len(transport) == 1
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = GeminiDialogueTTS(
        api_key="offline-key",
        speaker_voices={"One": "Puck", "Two": "Kore"},
        default_speaker="One",
    )
    path = str(tmp_path / "speech.wav")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_gemini_dialogue")
    assert module.GeminiDialogueTTS is GeminiDialogueTTS


def test_labelled_turn_contract(transport, tmp_path):
    import json

    provider = GeminiDialogueTTS(
        api_key="offline-key",
        speaker_voices={"Joe": "Puck", "Jane": "Kore"},
        style="calm",
    )
    turns = (
        GeminiDialogueTurn(text="Hello", speaker="Joe", style="cheerful"),
        GeminiDialogueTurn(text="Hi", speaker="Jane"),
    )
    provider.predict(turns, str(tmp_path / "dialogue.wav"))
    request = transport[0]
    assert (
        str(request.url)
        == "https://generativelanguage.googleapis.com/v1beta/interactions"
    )
    assert request.headers["x-goog-api-key"] == "offline-key"
    payload = json.loads(request.content)
    assert payload["generation_config"]["speech_config"] == {
        "speakers": [
            {"speaker": "Joe", "voice": "Puck"},
            {"speaker": "Jane", "voice": "Kore"},
        ]
    }
    assert payload["input"][0]["content"] == [
        {
            "type": "text",
            "text": "Hello",
            "annotations": [
                {
                    "type": "speech_metadata",
                    "speaker": "Joe",
                    "style": "cheerful",
                }
            ],
        },
        {
            "type": "text",
            "text": "Hi",
            "annotations": [
                {"type": "speech_metadata", "speaker": "Jane", "style": "calm"}
            ],
        },
    ]
    assert payload["store"] is False


@pytest.mark.asyncio
async def test_structured_batches(transport, tmp_path):
    provider = GeminiDialogueTTS(
        api_key="offline-key", speaker_voices={"A": "Puck", "B": "Kore"}
    )
    turns = (
        GeminiDialogueTurn(text="One", speaker="A"),
        GeminiDialogueTurn(text="Two", speaker="B"),
    )
    path = str(tmp_path / "dialogue.wav")
    assert await provider.apredict(turns, path) == path
    assert provider.batch({turns: path}) == [path]
    assert await provider.abatch({turns: path}, max_concurrent=1) == [path]
    assert len(transport) == 3


@pytest.mark.parametrize(
    "settings",
    [
        {"speaker_voices": {"A": "Puck"}},
        {"speaker_voices": {"A": "Puck", "B": ""}},
        {"speaker_voices": {"A": "Puck", "B": "Kore"}, "voice": "Kore"},
        {
            "speaker_voices": {"A": "Puck", "B": "Kore"},
            "default_speaker": "Missing",
        },
    ],
)
def test_bad_bindings(settings):
    with pytest.raises(ValueError):
        GeminiDialogueTTS(api_key="offline-key", **settings)


@pytest.mark.parametrize(
    "turns",
    [
        (),
        "no default speaker",
        (GeminiDialogueTurn(text="Hi", speaker="Unknown"),),
    ],
)
def test_bad_turns_make_no_request(transport, tmp_path, turns):
    with pytest.raises(ValueError):
        GeminiDialogueTTS(
            api_key="offline-key", speaker_voices={"A": "Puck", "B": "Kore"}
        ).predict(turns, str(tmp_path / "bad.wav"))
    assert not transport
