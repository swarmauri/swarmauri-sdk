"""Implement Deepgram Aura REST synthesis, excluding Flux and WebSockets."""

from typing import Any, Literal

import httpx
from pydantic import Field, SecretStr, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "DeepgramTTS")
class DeepgramTTS(HttpTTSMixin, TTSBase):
    """Use Aura voice-model IDs and validated encoding/container queries."""

    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=60, gt=0)
    allowed_models: list[str] = [
        "aura-2-thalia-en",
        "aura-2-andromeda-en",
        "aura-2-selena-es",
    ]
    name: str = "aura-2-thalia-en"
    type: Literal["DeepgramTTS"] = "DeepgramTTS"
    encoding: Literal["mp3", "linear16", "flac", "mulaw", "alaw"] = "mp3"
    container: Literal["wav", "none"] | None = None
    sample_rate: int | None = None

    @model_validator(mode="after")
    def _validate_format(self):
        if self.encoding in {"mp3", "flac"} and self.container is not None:
            raise ValueError("container applies to linear16, mulaw or alaw.")
        rates = {
            "mp3": set(),
            "linear16": {8000, 16000, 24000, 32000, 48000},
            "flac": {8000, 16000, 22050, 32000, 48000},
            "mulaw": {8000, 16000},
            "alaw": {8000, 16000},
        }
        if (
            self.sample_rate is not None
            and self.sample_rate not in rates[self.encoding]
        ):
            raise ValueError("sample_rate is unsupported for this encoding.")
        return self

    def _speech_endpoint(self, streaming: bool) -> str:
        params = {"model": self.name, "encoding": self.encoding}
        if self.encoding in {"linear16", "mulaw", "alaw"}:
            params["container"] = self.container or "wav"
        if self.sample_rate is not None:
            params["sample_rate"] = str(self.sample_rate)
        return str(
            httpx.URL("https://api.deepgram.com/v1/speak", params=params)
        )

    def _speech_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        return {"text": text}
