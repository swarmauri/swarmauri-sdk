import inspect

import pytest

from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_core.tts.ITextToSpeech import ITextToSpeech


pytestmark = pytest.mark.unit


def test_tts_base_implements_text_to_speech_interface() -> None:
    assert issubclass(TTSBase, ITextToSpeech)
    assert inspect.isabstract(TTSBase)
    assert TTSBase.model_fields["resource"].default == ResourceTypes.TTS.value
    assert TTSBase.model_fields["type"].default == "TTSBase"
