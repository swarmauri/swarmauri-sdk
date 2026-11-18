"""Share binary HTTP transport without coupling TTS provider packages."""

import asyncio
from collections.abc import AsyncIterator, Iterator, Mapping
from pathlib import Path
from typing import Any, ClassVar

import httpx


class HttpTTSMixin:
    """Implement file, streaming and bounded batch execution for speech APIs.

    Providers supply their fixed URL and payload. Requests are not retried
    automatically: replaying a speech request can generate duplicate charges.
    """

    _speech_url: ClassVar[str]
    _sse_stream: ClassVar[bool] = False

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        raise NotImplementedError

    def _speech_endpoint(self, streaming: bool) -> str:
        """Select a provider-owned URL without accepting credential redirects."""
        return self._speech_url

    def _speech_request(
        self, payload: dict[str, Any], streaming: bool
    ) -> dict[str, Any]:
        """Prepare the exact headers/body once, allowing XML and signing."""
        return {"headers": self._speech_headers(), "json": payload}

    def _audio_content(self, response: httpx.Response) -> bytes:
        """Extract unary audio; JSON providers override this decoding hook."""
        return response.content

    def _speech_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    def _payload(self, text: str, streaming: bool) -> dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Speech input must be non-empty text.")
        return self._speech_payload(text, streaming)

    def _check_response(
        self, response: httpx.Response, streaming: bool = False
    ) -> None:
        response.raise_for_status()
        media_type = (
            response.headers.get("content-type", "")
            .partition(";")[0]
            .strip()
            .lower()
        )
        if streaming and self._sse_stream:
            if media_type != "text/event-stream":
                raise ValueError("Expected an SSE audio response.")
        elif "json" in media_type or media_type.startswith("text/"):
            raise ValueError(
                "Expected binary audio, received a text response."
            )

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        payload = self._payload(text, streaming=False)
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self._speech_endpoint(False),
                **self._speech_request(payload, False),
            )
            self._check_response(response)
            content = self._audio_content(response)
        if not content:
            raise ValueError("Speech API returned empty audio.")
        path = Path(audio_path).expanduser().resolve()
        path.write_bytes(content)
        return str(path)

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        payload = self._payload(text, streaming=False)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._speech_endpoint(False),
                **self._speech_request(payload, False),
            )
            self._check_response(response)
            content = self._audio_content(response)
        if not content:
            raise ValueError("Speech API returned empty audio.")
        path = Path(audio_path).expanduser().resolve()
        path.write_bytes(content)
        return str(path)

    def _audio_chunks(self, response: httpx.Response) -> Iterator[bytes]:
        yield from response.iter_bytes()

    async def _async_audio_chunks(
        self, response: httpx.Response
    ) -> AsyncIterator[bytes]:
        async for chunk in response.aiter_bytes():
            yield chunk

    def stream(self, text: str) -> Iterator[bytes]:
        payload = self._payload(text, streaming=True)
        received = False
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream(
                "POST",
                self._speech_endpoint(True),
                **self._speech_request(payload, True),
            ) as response:
                self._check_response(response, streaming=True)
                for chunk in self._audio_chunks(response):
                    if chunk:
                        received = True
                        yield chunk
        if not received:
            raise ValueError("Speech API returned empty audio.")

    async def astream(self, text: str) -> AsyncIterator[bytes]:
        payload = self._payload(text, streaming=True)
        received = False
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self._speech_endpoint(True),
                **self._speech_request(payload, True),
            ) as response:
                self._check_response(response, streaming=True)
                async for chunk in self._async_audio_chunks(response):
                    if chunk:
                        received = True
                        yield chunk
        if not received:
            raise ValueError("Speech API returned empty audio.")

    def batch(self, text_path_dict: Mapping[str, str]) -> list[str]:
        return [
            self.predict(text, path) for text, path in text_path_dict.items()
        ]

    async def abatch(
        self, text_path_dict: Mapping[str, str], max_concurrent: int = 5
    ) -> list[str]:
        if (
            isinstance(max_concurrent, bool)
            or not isinstance(max_concurrent, int)
            or max_concurrent < 1
        ):
            raise ValueError("max_concurrent must be a positive integer.")
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate(text: str, path: str) -> str:
            async with semaphore:
                return await self.apredict(text, path)

        return await asyncio.gather(
            *(generate(text, path) for text, path in text_path_dict.items())
        )

    def get_allowed_models(self) -> list[str]:
        return list(self.allowed_models)
