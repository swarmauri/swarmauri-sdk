"""Use Azure's public regional Speech REST API with safely generated SSML."""

import re
from typing import Any, Literal
from xml.etree.ElementTree import Element, SubElement, tostring

from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "AzureTTS")
class AzureTTS(HttpTTSMixin, TTSBase):
    """Synthesize plain text with stock voices; no custom voice deployments."""

    api_key: SecretStr = Field(repr=False, min_length=1)
    region: str = Field(default="eastus", pattern=r"^[a-z][a-z0-9]{0,39}$")
    timeout: float = Field(default=60, gt=0)
    allowed_models: list[str] = [
        "en-US-JennyNeural",
        "en-US-AriaNeural",
        "en-US-GuyNeural",
    ]
    name: str = Field(default="en-US-JennyNeural", min_length=1)
    locale: str = Field(
        default="en-US", pattern=r"^[A-Za-z]{2,3}-[A-Za-z0-9-]+$"
    )
    output_format: Literal[
        "audio-24khz-48kbitrate-mono-mp3",
        "riff-24khz-16bit-mono-pcm",
        "raw-24khz-16bit-mono-pcm",
        "raw-8khz-8bit-mono-mulaw",
        "ogg-24khz-16bit-mono-opus",
    ] = "audio-24khz-48kbitrate-mono-mp3"
    type: Literal["AzureTTS"] = "AzureTTS"

    def _speech_endpoint(self, streaming: bool) -> str:
        return f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"

    def _speech_headers(self) -> dict[str, str]:
        return {
            "Ocp-Apim-Subscription-Key": self.api_key.get_secret_value(),
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": self.output_format,
            "User-Agent": "swarmauri_tts_azure/0.1.0a1",
        }

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        if re.search(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]", text
        ):
            raise ValueError(
                "Speech input contains characters invalid in XML."
            )
        root = Element(
            "speak",
            {
                "version": "1.0",
                "xmlns": "http://www.w3.org/2001/10/synthesis",
                "xml:lang": self.locale,
            },
        )
        SubElement(root, "voice", {"name": self.name}).text = text
        return {"ssml": tostring(root, encoding="utf-8")}

    def _speech_request(
        self, payload: dict[str, Any], streaming: bool
    ) -> dict[str, Any]:
        return {"headers": self._speech_headers(), "content": payload["ssml"]}
