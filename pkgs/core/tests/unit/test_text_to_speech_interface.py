import inspect

import pytest

from swarmauri_core.tts.ITextToSpeech import ITextToSpeech


pytestmark = pytest.mark.unit


def test_text_to_speech_interface_is_abstract() -> None:
    assert inspect.isabstract(ITextToSpeech)


def test_text_to_speech_interface_methods() -> None:
    expected = {"predict", "apredict", "stream", "astream", "batch", "abatch"}

    assert expected.issubset(ITextToSpeech.__abstractmethods__)
    assert list(inspect.signature(ITextToSpeech.predict).parameters) == [
        "self",
        "text",
        "audio_path",
    ]
