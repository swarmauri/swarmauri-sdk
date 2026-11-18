"""Provide the DeepInfra Audio Speech API, excluding native model APIs."""

from typing import Any, ClassVar, Literal

from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "DeepInfraTTS")
class DeepInfraTTS(HttpTTSMixin, TTSBase):
    """Generate audio through DeepInfra's documented /v1/audio/speech API.

    Model availability and voices require live verification. Native inference,
    cloning and voice-design operations are outside this component's scope.
    """

    _speech_url: ClassVar[str] = "https://api.deepinfra.com/v1/audio/speech"
    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=60.0, gt=0)
    allowed_models: list[str] = [
        "hexgrad/Kokoro-82M",
        "ResembleAI/chatterbox-turbo",
        "ResembleAI/chatterbox-multilingual",
        "canopylabs/orpheus-3b-0.1-ft",
    ]
    name: str = "hexgrad/Kokoro-82M"
    voice: str | None = Field(default=None, min_length=1)
    type: Literal["DeepInfraTTS"] = "DeepInfraTTS"
    response_format: Literal["mp3", "opus", "flac", "wav", "pcm"] = "mp3"
    speed: float = Field(default=1.0, ge=0.25, le=4)

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        payload = {
            "model": self.name,
            "input": text,
            "response_format": self.response_format,
            "speed": self.speed,
        }
        if self.voice is not None:
            payload["voice"] = self.voice
        return payload
