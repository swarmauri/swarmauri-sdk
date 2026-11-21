"""Preserve the old standard import for the standalone OpenAI TTS provider."""

import warnings

from swarmauri_tts_openai import OpenaiTTS

warnings.warn(
    "swarmauri_standard.tts.OpenaiTTS is deprecated; "
    "import OpenaiTTS from swarmauri_tts_openai instead.",
    FutureWarning,
    stacklevel=2,
)

__all__ = ["OpenaiTTS"]
