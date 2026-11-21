"""Preserve the deprecated LLM-named OpenAI speech component."""

import warnings
from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_tts_openai import OpenaiTTS

warnings.warn(
    "OpenAIAudioTTS is deprecated; use OpenaiTTS from swarmauri_tts_openai.",
    FutureWarning,
    stacklevel=2,
)


@ComponentBase.register_type(LLMBase, "OpenAIAudioTTS")
class OpenAIAudioTTS(OpenaiTTS, LLMBase):
    "Keep legacy type/resource serialization while sharing speech behavior."

    type: Literal["OpenAIAudioTTS"] = "OpenAIAudioTTS"
    resource: str | None = Field(default=ResourceTypes.LLM.value, frozen=True)
    timeout: float = Field(default=600.0, gt=0)
