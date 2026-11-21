"""Native DeepInfra synthesis, isolated from OpenAI speech."""

from typing import Any, ClassVar, Literal
import httpx
from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.JsonAudioTTSMixin import JsonAudioTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "DeepInfraQwen3TTS")
class DeepInfraQwen3TTS(JsonAudioTTSMixin, TTSBase):
    """Decode native JSON audio; streaming is intentionally unsupported."""

    _speech_url: ClassVar[str] = (
        "https://api.deepinfra.com/v1/inference/Qwen/Qwen3-TTS"
    )
    api_key: SecretStr = Field(repr=False, min_length=1)
    timeout: float = Field(default=120, gt=0)
    allowed_models: list[str] = ["Qwen/Qwen3-TTS"]
    name: str = Field(default="Qwen/Qwen3-TTS", min_length=1)
    type: Literal["DeepInfraQwen3TTS"] = "DeepInfraQwen3TTS"
    response_format: Literal["mp3", "opus", "flac", "wav", "pcm"] = "wav"
    language: Literal[
        "Auto",
        "Chinese",
        "English",
        "Japanese",
        "Korean",
        "German",
        "French",
        "Russian",
        "Portuguese",
        "Spanish",
        "Italian",
    ] = "Auto"
    voice: str = Field(default="Vivian", min_length=1)
    instruct: str | None = Field(default=None, min_length=1)

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        if len(text) > 4000:
            raise ValueError(
                "Input exceeds this native model's character limit."
            )
        payload = {
            "input": text,
            "voice": self.voice,
            "language": self.language,
            "response_format": self.response_format,
        }
        if self.instruct is not None:
            payload["instruct"] = self.instruct
        return payload

    def _audio_object(self, response: httpx.Response) -> dict[str, Any]:
        data = super()._audio_object(response)
        status = data.get("inference_status", {})
        if (
            not isinstance(status, dict)
            or status.get("status", "succeeded") != "succeeded"
        ):
            raise RuntimeError("Native speech inference did not succeed.")
        if data.get("output_format") not in (None, "", self.response_format):
            raise ValueError(
                "Native speech output format differs from the request."
            )
        return data
