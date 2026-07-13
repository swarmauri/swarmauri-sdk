import asyncio
import importlib
import json
from importlib.metadata import entry_points, version
from pathlib import Path
from typing import Any

import httpx
import pytest

from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_tts_playht import PlayHTModel, __version__


pytestmark = pytest.mark.unit

playht_module = importlib.import_module("swarmauri_tts_playht.PlayHTModel")


class FakeResponse:
    def __init__(
        self,
        *,
        content: bytes = b"audio-bytes",
        json_data: Any = None,
        status_code: int = 200,
    ) -> None:
        self.content = content
        self._json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.request = httpx.Request("GET", "https://api.play.ht/test")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "provider error", request=self.request, response=self
            )

    def json(self) -> Any:
        return self._json_data


@pytest.fixture
def voices() -> dict[str, list[dict[str, str]]]:
    return {
        "PlayDialog": [],
        "Play3.0-mini": [],
        "PlayHT2.0-turbo": [{"voice-id": "Adolfo"}],
        "PlayHT1.0": [],
        "PlayHT2.0": [{"fallback-id": "Fallback"}],
    }


@pytest.fixture
def model(
    monkeypatch: pytest.MonkeyPatch,
    voices: dict[str, list[dict[str, str]]],
) -> PlayHTModel:
    monkeypatch.setattr(
        PlayHTModel, "_fetch_prebuilt_voices", lambda self: voices
    )
    return PlayHTModel(
        api_key="test-key",
        user_id="test-user",
        name="PlayHT2.0-turbo",
        voice="Adolfo",
        timeout=42,
    )


def test_import_and_inheritance() -> None:
    assert PlayHTModel.__name__ == "PlayHTModel"
    assert issubclass(PlayHTModel, TTSBase)


def test_resource(model: PlayHTModel) -> None:
    assert model.resource == "TTS"


def test_type(model: PlayHTModel) -> None:
    assert model.type == "PlayHTModel"


def test_configuration(model: PlayHTModel) -> None:
    assert model.name == "PlayHT2.0-turbo"
    assert model.voice == "Adolfo"
    assert model.output_format == "mp3"
    assert model.timeout == 42
    assert model.allowed_models == [
        "PlayDialog",
        "Play3.0-mini",
        "PlayHT2.0-turbo",
        "PlayHT1.0",
        "PlayHT2.0",
    ]


def test_headers_use_credentials(model: PlayHTModel) -> None:
    assert model._headers == {
        "accept": "audio/mpeg",
        "content-type": "application/json",
        "AUTHORIZATION": "test-key",
        "X-USER-ID": "test-user",
    }


def test_serialization_round_trip(model: PlayHTModel) -> None:
    serialized = model.model_dump_json()
    restored = PlayHTModel.model_validate_json(serialized)

    assert "test-key" not in serialized
    assert restored.id == model.id
    assert restored.resource == "TTS"
    assert restored.type == "PlayHTModel"
    assert restored.name == model.name
    assert restored.voice == model.voice
    assert restored.timeout == model.timeout


def test_rejects_unknown_model(
    monkeypatch: pytest.MonkeyPatch,
    voices: dict[str, list[dict[str, str]]],
) -> None:
    monkeypatch.setattr(
        PlayHTModel, "_fetch_prebuilt_voices", lambda self: voices
    )

    with pytest.raises(ValueError, match="unknown-model is not allowed"):
        PlayHTModel(
            api_key="test-key",
            user_id="test-user",
            name="unknown-model",
        )


def test_rejects_unknown_voice(
    monkeypatch: pytest.MonkeyPatch,
    voices: dict[str, list[dict[str, str]]],
) -> None:
    monkeypatch.setattr(
        PlayHTModel, "_fetch_prebuilt_voices", lambda self: voices
    )

    with pytest.raises(ValueError, match="Voice name Unknown"):
        PlayHTModel(
            api_key="test-key",
            user_id="test-user",
            name="PlayHT2.0-turbo",
            voice="Unknown",
        )


def test_voice_lookup_includes_playht_2_fallback(model: PlayHTModel) -> None:
    assert model.allowed_voices == ["Adolfo", "Fallback"]
    assert model._get_voice_id("Adolfo") == "voice-id"
    assert model._get_voice_id("Fallback") == "fallback-id"

    with pytest.raises(ValueError, match="not found"):
        model._get_voice_id("Unknown")


def test_get_allowed_models(model: PlayHTModel) -> None:
    assert model.get_allowed_models() == [
        "Play3.0-mini",
        "PlayHT2.0-turbo",
        "PlayHT1.0",
        "PlayHT2.0",
    ]


def test_fetch_prebuilt_and_cloned_voices(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client"] = kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, path: str, **kwargs: Any) -> FakeResponse:
            captured["get"] = (path, kwargs)
            return FakeResponse(
                json_data=[
                    {
                        "id": "voice-id",
                        "name": "Adolfo",
                        "voice_engine": "Play3.0-mini",
                    },
                    {
                        "id": "ignored-id",
                        "name": "Ignored",
                        "voice_engine": "unsupported",
                    },
                ]
            )

    monkeypatch.setattr(playht_module.httpx, "Client", FakeClient)
    monkeypatch.setattr(
        PlayHTModel,
        "get_cloned_voices",
        lambda self: [{"id": "clone-id", "name": "Clone"}],
    )

    discovered = PlayHTModel(
        api_key="test-key",
        user_id="test-user",
        voice="Adolfo",
        timeout=17,
    )

    assert discovered.allowed_voices == ["Adolfo", "Clone"]
    assert captured["client"] == {
        "base_url": "https://api.play.ht/api/v2",
        "timeout": 17,
    }
    assert captured["get"][0] == "/voices"


def test_predict_writes_audio_and_sends_payload(
    model: PlayHTModel,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client"] = kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def post(self, path: str, **kwargs: Any) -> FakeResponse:
            captured["post"] = (path, kwargs)
            return FakeResponse(content=b"generated-audio")

    monkeypatch.setattr(playht_module.httpx, "Client", FakeClient)
    output = tmp_path / "speech.mp3"

    result = model.predict("Hello", str(output))

    assert result == str(output.resolve())
    assert output.read_bytes() == b"generated-audio"
    assert captured["client"]["timeout"] == 42
    path, request = captured["post"]
    assert path == "/tts/stream"
    assert request["json"] == {
        "voice": "voice-id",
        "output_format": "mp3",
        "voice_engine": "PlayHT2.0-turbo",
        "text": "Hello",
    }
    assert request["headers"]["accept"] == "audio/mpeg"


def test_predict_wraps_provider_errors(
    model: PlayHTModel,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FailingClient:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "FailingClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def post(self, path: str, **kwargs: Any) -> FakeResponse:
            return FakeResponse(status_code=500)

    monkeypatch.setattr(playht_module.httpx, "Client", FailingClient)

    with pytest.raises(RuntimeError, match="Text-to-Speech synthesis failed"):
        model.predict("Hello", str(tmp_path / "speech.mp3"))


@pytest.mark.asyncio
async def test_apredict_writes_audio(
    model: PlayHTModel,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}

    class FakeAsyncClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client"] = kwargs

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, path: str, **kwargs: Any) -> FakeResponse:
            captured["post"] = (path, kwargs)
            return FakeResponse(content=b"async-audio")

    monkeypatch.setattr(playht_module.httpx, "AsyncClient", FakeAsyncClient)
    output = tmp_path / "async.mp3"

    result = await model.apredict("Async hello", str(output))

    assert result == str(output.resolve())
    assert output.read_bytes() == b"async-audio"
    assert captured["client"]["timeout"] == 42
    assert captured["post"][1]["json"]["text"] == "Async hello"


def test_batch_preserves_input_order(
    model: PlayHTModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_predict(self: PlayHTModel, text: str, path: str) -> str:
        calls.append((text, path))
        return path

    monkeypatch.setattr(PlayHTModel, "predict", fake_predict)

    assert model.batch({"One": "one.mp3", "Two": "two.mp3"}) == [
        "one.mp3",
        "two.mp3",
    ]
    assert calls == [("One", "one.mp3"), ("Two", "two.mp3")]


@pytest.mark.asyncio
async def test_abatch_honors_concurrency_limit(
    model: PlayHTModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    active = 0
    peak = 0

    async def fake_apredict(self: PlayHTModel, text: str, path: str) -> str:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0)
        active -= 1
        return path

    monkeypatch.setattr(PlayHTModel, "apredict", fake_apredict)
    inputs = {f"Text {index}": f"{index}.mp3" for index in range(5)}

    assert await model.abatch(inputs, max_concurrent=2) == [
        f"{index}.mp3" for index in range(5)
    ]
    assert peak == 2


def test_stream_is_not_supported(model: PlayHTModel) -> None:
    with pytest.raises(NotImplementedError, match="Stream method"):
        model.stream("Hello")


@pytest.mark.asyncio
async def test_astream_is_not_supported(model: PlayHTModel) -> None:
    with pytest.raises(NotImplementedError, match="AStream method"):
        await model.astream("Hello")


def test_clone_voice_from_file(
    model: PlayHTModel,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client"] = kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def post(self, path: str, **kwargs: Any) -> FakeResponse:
            filename, sample, media_type = kwargs["files"]["sample_file"]
            captured["request"] = {
                "path": path,
                "data": kwargs["data"],
                "filename": filename,
                "sample": sample.read(),
                "media_type": media_type,
            }
            return FakeResponse(json_data={"id": "clone-id"})

    monkeypatch.setattr(playht_module.httpx, "Client", FakeClient)
    sample = tmp_path / "sample.mp4"
    sample.write_bytes(b"voice-sample")

    result = model.clone_voice_from_file("My Voice", str(sample))

    assert result == {"id": "clone-id"}
    assert captured["client"]["timeout"] == 42
    assert captured["request"] == {
        "path": "/cloned-voices/instant",
        "data": {"voice_name": "My Voice"},
        "filename": "sample.mp4",
        "sample": b"voice-sample",
        "media_type": "audio/mp4",
    }


def test_voice_management_endpoints(
    model: PlayHTModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, str, dict[str, Any]]] = []

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def post(self, path: str, **kwargs: Any) -> FakeResponse:
            calls.append(("POST", path, kwargs))
            return FakeResponse(json_data={"id": "clone-id"})

        def delete(self, path: str, **kwargs: Any) -> FakeResponse:
            calls.append(("DELETE", path, kwargs))
            return FakeResponse(json_data={"message": "deleted"})

        def get(self, path: str, **kwargs: Any) -> FakeResponse:
            calls.append(("GET", path, kwargs))
            return FakeResponse(
                json_data=[{"id": "clone-id", "name": "My Voice"}]
            )

    monkeypatch.setattr(playht_module.httpx, "Client", FakeClient)

    assert model.clone_voice_from_url(
        "My Voice", "https://example.com/sample.mp3"
    ) == {"id": "clone-id"}
    assert model.delete_cloned_voice("clone-id") == {"message": "deleted"}
    assert model.get_cloned_voices() == [
        {"id": "clone-id", "name": "My Voice"}
    ]

    assert [(method, path) for method, path, _ in calls] == [
        ("POST", "/cloned-voices/instant"),
        ("DELETE", "/cloned-voices"),
        ("GET", "/cloned-voices"),
    ]
    assert calls[1][2]["json"] == {"voice_id": "clone-id"}


def test_voice_management_returns_error_on_request_failure(
    model: PlayHTModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FailingClient:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "FailingClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, path: str, **kwargs: Any) -> FakeResponse:
            raise httpx.RequestError(
                "network unavailable",
                request=httpx.Request("GET", "https://api.play.ht"),
            )

    monkeypatch.setattr(playht_module.httpx, "Client", FailingClient)

    assert model.get_cloned_voices() == {"error": "network unavailable"}


def test_package_version() -> None:
    assert __version__ == version("swarmauri_tts_playht")


def test_tts_entry_point() -> None:
    providers = entry_points(group="swarmauri.tts")
    entry_point = next(
        item for item in providers if item.name == "PlayHTModel"
    )

    assert entry_point.value == "swarmauri_tts_playht:PlayHTModel"
