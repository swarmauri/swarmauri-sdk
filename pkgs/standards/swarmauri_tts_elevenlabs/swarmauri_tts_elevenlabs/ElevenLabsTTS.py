"""Implement ElevenLabs single-speaker speech endpoints."""

from typing import Any, Literal

import httpx
from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "ElevenLabsTTS")
class ElevenLabsTTS(HttpTTSMixin, TTSBase):
    """Keep unary and streaming routes distinct from Text-to-Dialogue."""

    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=60, gt=0)
    allowed_models: list[str] = ["eleven_multilingual_v2", "eleven_flash_v2_5"]
    name: str = "eleven_multilingual_v2"
    voice: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")
    type: Literal["ElevenLabsTTS"] = "ElevenLabsTTS"
    output_format: Literal["mp3_44100_128", "pcm_24000", "ulaw_8000"] = (
        "mp3_44100_128"
    )
    stability: float | None = Field(default=None, ge=0, le=1)
    similarity_boost: float | None = Field(default=None, ge=0, le=1)

    def _speech_endpoint(self, streaming: bool) -> str:
        suffix = "/stream" if streaming else ""
        url = httpx.URL(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice}{suffix}"
        )
        return str(url.copy_add_param("output_format", self.output_format))

    def _speech_headers(self) -> dict[str, str]:
        return {
            "xi-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        payload = {"text": text, "model_id": self.name}
        settings = {
            key: value
            for key, value in {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
            }.items()
            if value is not None
        }
        if settings:
            payload["voice_settings"] = settings
        return payload
