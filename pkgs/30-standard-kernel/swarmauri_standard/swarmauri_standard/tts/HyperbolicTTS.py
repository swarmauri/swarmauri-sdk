"""Preserve imports for Hyperbolic's decommissioned audio endpoint."""

import warnings
from typing import Literal
from pydantic import SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.TTSBase import TTSBase

RETIRED_MESSAGE = (
    "Hyperbolic's legacy api.hyperbolic.xyz/v1 audio endpoint was "
    "decommissioned. HyperbolicTTS and HyperbolicAudioTTS are deprecated. "
    "Choose a standalone alpha TTS provider using docs/migrations/playht.md; "
    "old credentials and voice settings are not redirected to another service."
)


def _retired():
    warnings.warn(RETIRED_MESSAGE, FutureWarning, stacklevel=3)
    raise RuntimeError(RETIRED_MESSAGE)


@ComponentBase.register_type(TTSBase, "HyperbolicTTS")
class HyperbolicTTS(TTSBase):
    """Compatibility type only; construction and execution fail locally."""

    api_key: SecretStr | None = None
    language: str | None = None
    speaker: str | None = None
    speed: float | None = 1.0
    type: Literal["HyperbolicTTS"] = "HyperbolicTTS"
    allowed_languages: list[str] = ["EN", "ES", "FR", "ZH", "JP", "KR"]
    allowed_speakers: dict[str, list[str]] = {
        "EN": ["EN-US", "EN-BR", "EN-INDIA", "EN-AU"],
        "ES": ["ES"],
        "FR": ["FR"],
        "ZH": ["ZH"],
        "JP": ["JP"],
        "KR": ["KR"],
    }

    def __init__(self, **data):
        _retired()

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        _retired()

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        _retired()

    def batch(self, text_path_dict):
        _retired()

    async def abatch(self, text_path_dict, max_concurrent: int = 5):
        _retired()

    def stream(self, text: str, audio_path: str = "output.mp3"):
        _retired()

    async def astream(self, text: str, audio_path: str = "output.mp3"):
        _retired()
