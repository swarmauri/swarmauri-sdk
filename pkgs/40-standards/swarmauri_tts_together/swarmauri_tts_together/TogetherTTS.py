"""Provide Together speech files and decoded SSE audio streams."""

import base64
import binascii
import json
from collections.abc import AsyncIterator, Iterator
from typing import Any, ClassVar, Literal

import httpx
from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


def _audio_event(data: str) -> tuple[bool, bytes]:
    """Decode an SSE audio event; never return event framing to callers."""
    if data.strip() == "[DONE]":
        return True, b""
    try:
        event = json.loads(data)
        if not isinstance(event, dict):
            raise ValueError("Expected an SSE JSON object.")
        if "error" in event or event.get("type") == "error":
            raise RuntimeError("Together speech stream reported an error.")
        if event.get("type") == "conversation.item.audio_output.delta":
            return False, base64.b64decode(event["delta"], validate=True)
    except (ValueError, KeyError, TypeError, binascii.Error) as exc:
        raise ValueError("Invalid Together audio event.") from exc
    return False, b""


@ComponentBase.register_type(TTSBase, "TogetherTTS")
class TogetherTTS(HttpTTSMixin, TTSBase):
    """Write MP3/WAV/raw files; stream decoded PCM rather than SSE text."""

    _speech_url: ClassVar[str] = "https://api.together.ai/v1/audio/speech"
    _sse_stream: ClassVar[bool] = True
    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=60.0, gt=0)
    allowed_models: list[str] = [
        "canopylabs/orpheus-3b-0.1-ft",
        "hexgrad/Kokoro-82M",
    ]
    name: str = "canopylabs/orpheus-3b-0.1-ft"
    voice: str = Field(default="tara", min_length=1)
    type: Literal["TogetherTTS"] = "TogetherTTS"
    response_format: Literal["mp3", "wav", "raw"] = "mp3"
    sample_rate: int = Field(default=24000, gt=0)

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        output_format = "raw" if streaming else self.response_format
        payload = {
            "model": self.name,
            "input": text,
            "voice": self.voice,
            "response_format": output_format,
            "sample_rate": self.sample_rate,
            "stream": streaming,
        }
        if output_format == "raw":
            payload["response_encoding"] = "pcm_s16le"
        return payload

    def _audio_chunks(self, response: httpx.Response) -> Iterator[bytes]:
        data: list[str] = []
        for line in response.iter_lines():
            if line.startswith("data:"):
                data.append(line[5:].lstrip())
            elif not line and data:
                done, audio = _audio_event("\n".join(data))
                data.clear()
                if done:
                    return
                if audio:
                    yield audio
        if data:
            done, audio = _audio_event("\n".join(data))
            if done:
                return
            if audio:
                yield audio
        raise ValueError("Together speech stream ended before [DONE].")

    async def _async_audio_chunks(
        self, response: httpx.Response
    ) -> AsyncIterator[bytes]:
        data: list[str] = []
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                data.append(line[5:].lstrip())
            elif not line and data:
                done, audio = _audio_event("\n".join(data))
                data.clear()
                if done:
                    return
                if audio:
                    yield audio
        if data:
            done, audio = _audio_event("\n".join(data))
            if done:
                return
            if audio:
                yield audio
        raise ValueError("Together speech stream ended before [DONE].")
