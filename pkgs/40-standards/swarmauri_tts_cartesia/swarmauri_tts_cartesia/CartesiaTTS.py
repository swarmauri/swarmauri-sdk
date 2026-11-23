"""Implement the versioned Cartesia Sonic bytes API."""

from typing import Any, ClassVar, Literal

from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "CartesiaTTS")
class CartesiaTTS(HttpTTSMixin, TTSBase):
    """Synthesize files and HTTP audio chunks; no WebSocket sessions."""

    _speech_url: ClassVar[str] = "https://api.cartesia.ai/tts/bytes"
    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=60, gt=0)
    allowed_models: list[str] = ["sonic-3.6", "sonic-3.5", "sonic-3"]
    name: str = "sonic-3.6"
    voice: str = Field(min_length=1)
    type: Literal["CartesiaTTS"] = "CartesiaTTS"
    api_version: Literal["2026-08-14"] = "2026-08-14"
    response_format: Literal["mp3", "wav", "raw"] = "mp3"
    sample_rate: Literal[8000, 16000, 22050, 24000, 44100, 48000] = 44100
    bit_rate: Literal[32000, 64000, 96000, 128000, 192000] = 128000
    speed: float | None = Field(default=None, ge=0.6, le=1.5)
    language: str | None = Field(default=None, min_length=1)

    def _speech_headers(self) -> dict[str, str]:
        return {
            **super()._speech_headers(),
            "Cartesia-Version": self.api_version,
        }

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        output = {
            "container": self.response_format,
            "sample_rate": self.sample_rate,
        }
        if self.response_format == "mp3":
            output["bit_rate"] = self.bit_rate
        else:
            output["encoding"] = "pcm_s16le"
        payload = {
            "model_id": self.name,
            "transcript": text,
            "voice": self.voice,
            "output_format": output,
        }
        if self.speed is not None:
            payload["generation_config"] = {"speed": self.speed}
        if self.language is not None:
            payload["language"] = self.language
        return payload
