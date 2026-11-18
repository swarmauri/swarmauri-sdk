"""Transport complete base64 audio in JSON without claiming incremental audio."""

import base64
import binascii
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx

from .HttpTTSMixin import HttpTTSMixin


class JsonAudioTTSMixin(HttpTTSMixin):
    """Decode an audio field; never fetch URLs returned by an audio service."""

    def _check_response(
        self, response: httpx.Response, streaming: bool = False
    ) -> None:
        response.raise_for_status()

    def _audio_object(self, response: httpx.Response) -> dict[str, Any]:
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON audio object.")
        if "error" in data:
            raise RuntimeError("Speech API reported an error.")
        return data

    def _audio_content(self, response: httpx.Response) -> bytes:
        data = self._audio_object(response)
        audio = data.get("audio")
        if not isinstance(audio, str) or not audio:
            raise ValueError("Speech API returned no encoded audio.")
        if audio.startswith("data:"):
            header, separator, audio = audio.partition(",")
            if (
                not separator
                or not header.startswith("data:audio/")
                or not header.endswith(";base64")
            ):
                raise ValueError("Expected a base64 audio data URI.")
        try:
            content = base64.b64decode(audio, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("Invalid base64 audio.") from exc
        if not content:
            raise ValueError("Speech API returned empty audio.")
        if getattr(self, "response_format", None) == "wav" and (
            content[:4] != b"RIFF" or content[8:12] != b"WAVE"
        ):
            raise ValueError("Expected WAV audio.")
        return content

    def predict(self, text: str, audio_path: str = "output.wav") -> str:
        return super().predict(text, audio_path)

    async def apredict(self, text: str, audio_path: str = "output.wav") -> str:
        return await super().apredict(text, audio_path)

    def stream(self, text: str) -> Iterator[bytes]:
        raise NotImplementedError(
            "This JSON audio adapter has no verified streaming contract."
        )

    async def astream(self, text: str) -> AsyncIterator[bytes]:
        for chunk in self.stream(text):
            yield chunk
