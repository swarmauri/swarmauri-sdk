"""Sign Amazon Polly REST requests without credential-discovery network I/O."""

import json
from typing import Any, Literal

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from pydantic import Field, SecretStr, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "PollyTTS")
class PollyTTS(HttpTTSMixin, TTSBase):
    """Use SynthesizeSpeech engines with explicit, optionally temporary keys.

    Only commercial AWS regions and plain text are supported. Speech marks,
    SSML, voice discovery and S3 synthesis jobs have separate contracts.
    """

    access_key_id: SecretStr = Field(repr=False, min_length=1)
    secret_access_key: SecretStr = Field(repr=False, min_length=1)
    session_token: SecretStr | None = Field(
        default=None, repr=False, min_length=1
    )
    region: str = Field(default="us-east-1", pattern=r"^[a-z]{2}-[a-z]+-\d+$")
    timeout: float = Field(default=60, gt=0)
    allowed_models: list[str] = [
        "standard",
        "neural",
        "long-form",
        "generative",
    ]
    name: str = Field(default="neural", min_length=1)
    voice: str = Field(default="Joanna", min_length=1)
    language_code: str | None = Field(default=None, min_length=1)
    response_format: Literal[
        "mp3", "ogg_vorbis", "ogg_opus", "pcm", "mulaw", "alaw"
    ] = "mp3"
    sample_rate: int | None = None
    type: Literal["PollyTTS"] = "PollyTTS"

    @model_validator(mode="after")
    def _validate_audio_format(self):
        if self.region.startswith("cn-"):
            raise ValueError(
                "This adapter supports commercial AWS regions only."
            )
        rates = {
            "mp3": {8000, 16000, 22050, 24000, 44100, 48000},
            "ogg_vorbis": {8000, 16000, 22050, 24000, 44100, 48000},
            "ogg_opus": {48000},
            "pcm": {8000, 16000},
            "mulaw": {8000},
            "alaw": {8000},
        }
        if (
            self.sample_rate is not None
            and self.sample_rate not in rates[self.response_format]
        ):
            raise ValueError(
                "sample_rate is unsupported for this output format."
            )
        return self

    def _speech_endpoint(self, streaming: bool) -> str:
        return f"https://polly.{self.region}.amazonaws.com/v1/speech"

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        payload = {
            "Text": text,
            "TextType": "text",
            "Engine": self.name,
            "VoiceId": self.voice,
            "OutputFormat": self.response_format,
        }
        if self.sample_rate is not None:
            payload["SampleRate"] = str(self.sample_rate)
        if self.language_code is not None:
            payload["LanguageCode"] = self.language_code
        return payload

    def _speech_request(
        self, payload: dict[str, Any], streaming: bool
    ) -> dict[str, Any]:
        body = json.dumps(
            payload, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        request = AWSRequest(
            method="POST",
            url=self._speech_endpoint(streaming),
            data=body,
            headers={"Content-Type": "application/json"},
        )
        credentials = Credentials(
            self.access_key_id.get_secret_value(),
            self.secret_access_key.get_secret_value(),
            self.session_token.get_secret_value()
            if self.session_token
            else None,
        )
        SigV4Auth(credentials, "polly", self.region).add_auth(request)
        return {"headers": dict(request.headers.items()), "content": body}
