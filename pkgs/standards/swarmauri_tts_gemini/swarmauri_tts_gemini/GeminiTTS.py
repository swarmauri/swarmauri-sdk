"""Implement single-speaker Gemini 3.8 TTS through Interactions only."""

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


def _decode_audio(data: Any) -> bytes:
    try:
        if not isinstance(data, str):
            raise ValueError("Expected base64 text.")
        return base64.b64decode(data, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Invalid Gemini audio data.") from exc


def _audio_event(data: str) -> tuple[bool, bytes]:
    try:
        event = json.loads(data)
        if not isinstance(event, dict):
            raise ValueError("Expected a JSON object.")
    except ValueError as exc:
        raise ValueError("Invalid Gemini SSE event.") from exc
    event_type = event.get("event_type")
    interaction = event.get("interaction", {})
    if not isinstance(interaction, dict):
        raise ValueError("Invalid Gemini interaction event.")
    if event_type == "error" or "error" in event:
        raise RuntimeError("Gemini speech stream reported an error.")
    if interaction.get("status") in {
        "failed",
        "cancelled",
        "incomplete",
        "requires_action",
        "budget_exceeded",
    }:
        raise RuntimeError("Gemini speech generation did not complete.")
    if event_type == "interaction.completed":
        return True, b""
    if event_type == "step.delta":
        delta = event.get("delta")
        if not isinstance(delta, dict):
            raise ValueError("Invalid Gemini step delta.")
        if delta.get("type") == "audio":
            mime = delta.get("mime_type", "audio/l16")
            if not isinstance(mime, str):
                raise ValueError("Invalid Gemini audio MIME type.")
            mime = mime.split(";")[0].lower()
            if mime != "audio/l16":
                raise ValueError("Expected raw PCM in the Gemini stream.")
            return False, _decode_audio(delta.get("data"))
    return False, b""


@ComponentBase.register_type(TTSBase, "GeminiTTS")
class GeminiTTS(HttpTTSMixin, TTSBase):
    """Write complete WAV files and decode streamed 24 kHz mono PCM.

    Older generateContent models, multi-speaker dialogue, voice creation and
    Gemini Live sessions have different contracts and are excluded here.
    """

    _speech_url: ClassVar[str] = (
        "https://generativelanguage.googleapis.com/v1beta/interactions"
    )
    _sse_stream: ClassVar[bool] = True
    sample_rate: ClassVar[int] = 24000
    stream_encoding: ClassVar[str] = "pcm_s16le"
    api_key: SecretStr = Field(repr=False)
    timeout: float = Field(default=120, gt=0)
    allowed_models: list[str] = [
        "gemini-3.8-flash-tts",
        "gemini-3.8-flash-lite-tts",
    ]
    name: str = "gemini-3.8-flash-tts"
    voice: str = Field(default="Kore", min_length=1)
    style: str | None = Field(default=None, min_length=1)
    type: Literal["GeminiTTS"] = "GeminiTTS"

    def _speech_headers(self) -> dict[str, str]:
        return {
            "x-goog-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        content = {"type": "text", "text": text}
        if self.style is not None:
            content["annotations"] = [
                {"type": "speech_metadata", "style": self.style}
            ]
        return {
            "model": self.name,
            "input": [{"type": "user_input", "content": [content]}],
            "response_format": {
                "type": "audio",
                "mime_type": "audio/l16" if streaming else "audio/wav",
                "sample_rate": self.sample_rate,
            },
            "generation_config": {"speech_config": [{"voice": self.voice}]},
            "stream": streaming,
            "store": False,
        }

    def _check_response(
        self, response: httpx.Response, streaming: bool = False
    ) -> None:
        if streaming:
            super()._check_response(response, streaming=True)
        else:
            response.raise_for_status()

    def _audio_content(self, response: httpx.Response) -> bytes:
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Expected a Gemini interaction object.")
        if "error" in data or data.get("status") != "completed":
            raise RuntimeError("Gemini speech generation did not complete.")
        audio = None
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError("Invalid Gemini output steps.")
        for step in steps:
            if isinstance(step, dict) and step.get("type") == "model_output":
                parts = step.get("content", [])
                if not isinstance(parts, list):
                    raise ValueError("Invalid Gemini output content.")
                for part in parts:
                    if isinstance(part, dict) and part.get("type") == "audio":
                        audio = part
        if audio is None:
            raise ValueError("Gemini returned no audio output.")
        content = _decode_audio(audio.get("data"))
        if content[:4] != b"RIFF" or content[8:12] != b"WAVE":
            raise ValueError("Expected a complete WAV file from Gemini.")
        return content

    def predict(self, text: str, audio_path: str = "output.wav") -> str:
        return super().predict(text, audio_path)

    async def apredict(self, text: str, audio_path: str = "output.wav") -> str:
        return await super().apredict(text, audio_path)

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
        raise ValueError("Gemini speech stream ended before completion.")

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
        raise ValueError("Gemini speech stream ended before completion.")
