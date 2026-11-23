"""Keep the legacy community import with explicit migration guidance."""

import warnings

from swarmauri_standard.llms.OpenAIAudioTTS import OpenAIAudioTTS

warnings.warn(
    "swarmauri_llm_openai.OpenAIAudioTTS is deprecated; "
    "use OpenaiTTS from swarmauri_tts_openai.",
    FutureWarning,
    stacklevel=2,
)

__all__ = ["OpenAIAudioTTS"]
