"""Offline package and documented request-contract tests."""

import importlib
from importlib.metadata import entry_points, metadata, version
from packaging.version import Version

import httpx
import pytest
from swarmauri_tts_elevenlabs_dialogue import (
    ElevenLabsDialogueTTS,
    DialogueTurn,
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
    assert __version__ == version("swarmauri_tts_elevenlabs_dialogue")
    assert Version(__version__).is_prerelease
    info = metadata("swarmauri_tts_elevenlabs_dialogue")
    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")
    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )
    point = next(
        p
        for p in entry_points(group="swarmauri.tts")
        if p.name == "ElevenLabsDialogueTTS"
    )
    assert point.load() is ElevenLabsDialogueTTS
    assert issubclass(ElevenLabsDialogueTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):
    provider = ElevenLabsDialogueTTS(
        api_key="offline-key", **{"default_voice_id": "voice-one"}
    )
    path = tmp_path / "speech.mp3"
    assert provider.predict("hello", str(path)) == str(path.resolve())
    assert path.read_bytes() == b"audio"
    assert len(transport) == 1
    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):
    provider = ElevenLabsDialogueTTS(
        api_key="offline-key", **{"default_voice_id": "voice-one"}
    )
    path = str(tmp_path / "speech.mp3")
    assert await provider.apredict("hello", path) == path
    assert provider.batch({"hello": path}) == [path]
    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]
    assert len(transport) == 3


def test_import_is_available_without_standard_package():
    module = importlib.import_module("swarmauri_tts_elevenlabs_dialogue")
    assert module.ElevenLabsDialogueTTS is ElevenLabsDialogueTTS


@pytest.mark.parametrize("text", ["", "  ", "x" * (2000 + 1)])
def test_invalid_text_is_local(transport, tmp_path, text):
    with pytest.raises(ValueError):
        ElevenLabsDialogueTTS(
            api_key="offline-key", **{"default_voice_id": "voice-one"}
        ).predict(text, str(tmp_path / "output.wav"))
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
        ElevenLabsDialogueTTS(
            **(
                {"api_key": "offline-key"}
                | {"default_voice_id": "voice-one"}
                | settings
            )
        )
    assert not transport


def test_ordered_turns_use_dialogue_route(transport, tmp_path):
    import json

    turns = (
        DialogueTurn(text="[curious] Hello?", voice_id="speaker-a"),
        DialogueTurn(text="Hello back!", voice_id="speaker-b"),
    )
    provider = ElevenLabsDialogueTTS(api_key="offline-key")
    provider.predict(turns, str(tmp_path / "dialogue.mp3"))
    request = transport[0]
    assert (
        str(request.url)
        == "https://api.elevenlabs.io/v1/text-to-dialogue?output_format=mp3_44100_128"
    )
    assert request.headers["xi-api-key"] == "offline-key"
    assert "authorization" not in request.headers
    assert json.loads(request.content) == {
        "model_id": "eleven_v4",
        "inputs": [
            {"text": "[curious] Hello?", "voice_id": "speaker-a"},
            {"text": "Hello back!", "voice_id": "speaker-b"},
        ],
    }
    assert (
        httpx.URL(provider._speech_endpoint(True)).path
        == "/v1/text-to-dialogue/stream"
    )


@pytest.mark.asyncio
async def test_structured_async_and_batches(transport, tmp_path):
    turns = (
        DialogueTurn(text="One", voice_id="a"),
        DialogueTurn(text="Two", voice_id="b"),
    )
    provider = ElevenLabsDialogueTTS(api_key="offline-key")
    path = str(tmp_path / "dialogue.mp3")
    assert await provider.apredict(turns, path) == path
    assert provider.batch({turns: path}) == [path]
    assert await provider.abatch({turns: path}, max_concurrent=1) == [path]
    assert len(transport) == 3


@pytest.mark.parametrize(
    "turns",
    [
        (),
        [],
        ({"text": "raw dict", "voice_id": "a"},),
        "needs-default-voice",
        tuple(
            DialogueTurn(text="hi", voice_id=f"voice-{i}") for i in range(11)
        ),
        (DialogueTurn(text="x" * 2001, voice_id="a"),),
    ],
)
def test_bad_dialogue_fails_locally(transport, tmp_path, turns):
    with pytest.raises(ValueError):
        ElevenLabsDialogueTTS(api_key="offline-key").predict(
            turns, str(tmp_path / "dialogue.mp3")
        )
    assert not transport


@pytest.mark.parametrize(
    "values",
    [
        {"text": " ", "voice_id": "a"},
        {"text": "hi", "voice_id": ""},
        {"text": "hi", "voice_id": "a", "unexpected": "no"},
    ],
)
def test_turn_validation(values):
    with pytest.raises(ValueError):
        DialogueTurn(**values)
