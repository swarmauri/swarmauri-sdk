import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


pytestmark = pytest.mark.unit


def test_text_to_speech_agent_is_first_class() -> None:
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.agents.TextToSpeechAgent"
        ]
        == "swarmauri_agent_texttospeech.TextToSpeechAgent"
    )
