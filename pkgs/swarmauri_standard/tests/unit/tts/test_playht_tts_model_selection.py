import pytest

from swarmauri_standard.tts.PlayhtTTS import PlayhtTTS


pytestmark = pytest.mark.unit


def test_playht_tts_preserves_selected_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    voices = {
        "PlayDialog": [],
        "Play3.0-mini": [],
        "PlayHT2.0-turbo": [{"voice-id": "Adolfo"}],
        "PlayHT1.0": [],
        "PlayHT2.0": [],
    }
    monkeypatch.setattr(
        PlayhtTTS,
        "_fetch_prebuilt_voices",
        lambda self: voices,
    )

    tts = PlayhtTTS(
        api_key="test-key",
        user_id="test-user",
        name="PlayHT2.0-turbo",
        voice="Adolfo",
    )

    assert tts.name == "PlayHT2.0-turbo"
