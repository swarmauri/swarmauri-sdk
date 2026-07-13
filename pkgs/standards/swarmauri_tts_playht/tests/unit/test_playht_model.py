from importlib.metadata import entry_points, version

import pytest

from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_tts_playht import PlayHTModel, __version__


pytestmark = pytest.mark.unit


@pytest.fixture
def voices() -> dict[str, list[dict[str, str]]]:
    return {
        "PlayDialog": [],
        "Play3.0-mini": [],
        "PlayHT2.0-turbo": [{"voice-id": "Adolfo"}],
        "PlayHT1.0": [],
        "PlayHT2.0": [],
    }


def test_playht_model_is_tts_base(
    monkeypatch: pytest.MonkeyPatch,
    voices: dict[str, list[dict[str, str]]],
) -> None:
    monkeypatch.setattr(
        PlayHTModel, "_fetch_prebuilt_voices", lambda self: voices
    )

    model = PlayHTModel(
        api_key="test-key",
        user_id="test-user",
        name="PlayHT2.0-turbo",
        voice="Adolfo",
        timeout=42,
    )

    assert isinstance(model, TTSBase)
    assert model.resource == "TTS"
    assert model.type == "PlayHTModel"
    assert model.name == "PlayHT2.0-turbo"
    assert model.timeout == 42


def test_package_version() -> None:
    assert __version__ == version("swarmauri_tts_playht")


def test_tts_entry_point() -> None:
    providers = entry_points(group="swarmauri.tts")
    entry_point = next(
        item for item in providers if item.name == "PlayHTModel"
    )

    assert entry_point.value == "swarmauri_tts_playht:PlayHTModel"
