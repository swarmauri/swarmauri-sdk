"""Provide the legacy standard-package name for the PlayHT TTS provider."""

from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_tts_playht import PlayHTModel


@ComponentBase.register_type(TTSBase, "PlayhtTTS")
class PlayhtTTS(PlayHTModel):
    """Preserve the historic PlayhtTTS import over the standalone provider."""

    type: Literal["PlayhtTTS"] = "PlayhtTTS"
