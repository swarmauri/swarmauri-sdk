"""Provide OpenAI speech synthesis as a standalone alpha component."""

import warnings
from typing import Any, ClassVar, Literal

from pydantic import Field, SecretStr, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "OpenaiTTS")
class OpenaiTTS(HttpTTSMixin, TTSBase):
    """Generate files or binary audio streams through OpenAI Audio Speech."""

    _speech_url: ClassVar[str] = "https://api.openai.com/v1/audio/speech"
    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=30.0, gt=0)
    allowed_models: list[str] = ["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
    allowed_voices: list[str] = [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
        "ash",
        "ballad",
        "coral",
        "sage",
        "verse",
        "marin",
        "cedar",
    ]
    name: str = "tts-1"
    voice: str = "alloy"
    type: Literal["OpenaiTTS"] = "OpenaiTTS"
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = (
        "mp3"
    )
    speed: float | None = Field(default=None, ge=0.25, le=4)
    instructions: str | None = None

    @model_validator(mode="after")
    def _validate_speech_settings(self):
        if self.voice not in self.allowed_voices:
            raise ValueError("Choose a supported OpenAI voice.")
        if self.instructions is not None and self.name in {
            "tts-1",
            "tts-1-hd",
        }:
            raise ValueError("instructions require gpt-4o-mini-tts.")
        return self

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        warnings.warn(
            "OpenAI Speech API models (including "
            + self.name
            + ") are deprecated "
            "and scheduled to shut down on 2027-01-06. The recommended "
            "gpt-realtime-2.1-mini uses the Realtime API "
            "and cannot be sent to "
            "this speech endpoint. See docs/migrations/openai-speech.md.",
            FutureWarning,
            stacklevel=3,
        )
        payload = {
            "model": self.name,
            "voice": self.voice,
            "input": text,
        }
        # Preserve the legacy default payload; OpenAI defaults to MP3.
        if self.response_format != "mp3":
            payload["response_format"] = self.response_format
        if self.speed is not None:
            payload["speed"] = self.speed
        if self.instructions is not None:
            payload["instructions"] = self.instructions
        return payload
