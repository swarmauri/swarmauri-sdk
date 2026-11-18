"""Provide the deprecated LLM-named import for the standalone TTS provider."""

import warnings

from swarmauri_tts_playht import PlayHTModel

warnings.warn(
    (
        "Play.ht has discontinued its TTS service. This provider is "
        "deprecated; use swarmauri_standard.tts.OpenaiTTS.OpenaiTTS "
        "with OPENAI_API_KEY, a supported OpenAI model, and an OpenAI "
        "voice. Play.ht credentials and voice IDs cannot be reused."
    ),
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PlayHTModel"]
