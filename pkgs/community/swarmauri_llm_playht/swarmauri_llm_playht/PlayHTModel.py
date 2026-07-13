"""Provide the deprecated LLM-named import for the standalone TTS provider."""

import warnings

from swarmauri_tts_playht import PlayHTModel

warnings.warn(
    "swarmauri_llm_playht is deprecated; install "
    "swarmauri_tts_playht instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PlayHTModel"]
