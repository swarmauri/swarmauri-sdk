"""Check that the standard kernel omits the OpenAI speech imports."""

import importlib.util

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "module",
    [
        "swarmauri_standard.tts.OpenaiTTS",
        "swarmauri_standard.llms.OpenAIAudioTTS",
    ],
)
def test_removed_openai_speech_modules(module):
    assert importlib.util.find_spec(module) is None
