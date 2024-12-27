import asyncio
import io
import os
from typing import AsyncIterator, Iterator, List, Literal, Dict
import httpx
from pydantic import PrivateAttr, model_validator
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.llms.LLMBase import LLMBase


class OpenAIAudioTTS(LLMBase):
    """
    A class to interact with OpenAI's Text-to-Speech API, allowing for synchronous
    and asynchronous text-to-speech synthesis, as well as streaming capabilities.

    Attributes:
        api_key (str): The API key for accessing OpenAI's TTS service.
        allowed_models (List[str]): List of models supported by the TTS service.
        allowed_voices (List[str]): List of available voices.
        name (str): The default model name used for TTS.
        type (Literal): The type of TTS model.
        voice (str): The default voice setting for TTS synthesis.

    Provider Resource: https://platform.openai.com/docs/guides/text-to-speech/overview

    """

    api_key: str
    allowed_models: List[str] = ["tts-1", "tts-1-hd"]

    allowed_voices: List[str] = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    name: str = "tts-1"
    type: Literal["OpenAIAudioTTS"] = "OpenAIAudioTTS"
    voice: str = "alloy"
    _BASE_URL: str = PrivateAttr(default="https://api.openai.com/v1/audio/speech")
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data):
        """
        Initialize the OpenAIAudioTTS class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @model_validator(mode="after")
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        """
        Validate that the provided voice name is in the list of allowed voices.

        Args:
            values: The values provided during model initialization.

        Returns:
            dict: The validated values.

        Raises:
            ValueError: If the voice name is not in the allowed voices.
        """
        voice = values.voice
        allowed_voices = values.allowed_voices
        if voice and voice not in allowed_voices:
            raise ValueError(
                f"Model name {voice} is not allowed. Choose from {allowed_voices}"
            )
        return values

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Synchronously converts text to speech using httpx.

        Parameters:
            text (str): The text to convert to speech.
            audio_path (str): Path to save the synthesized audio.
        Returns:
            str: Absolute path to the saved audio file.
        """
        payload = {"model": self.name, "voice": self.voice, "input": text}

        with httpx.Client(timeout=30) as client:
            response = client.post(self._BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()

            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)
            return os.path.abspath(audio_path)

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Asynchronously converts text to speech using httpx.

        Parameters:
            text (str): The text to convert to speech.
            audio_path (str): Path to save the synthesized audio.
        Returns:
            str: Absolute path to the saved audio file.
        """
        payload = {"model": self.name, "voice": self.voice, "input": text}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self._BASE_URL, headers=self._headers, json=payload
            )

            response.raise_for_status()
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)
            return os.path.abspath(audio_path)

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(self, text: str) -> Iterator[bytes]:
        """
        Synchronously streams TTS audio using httpx.

        Parameters:
            text (str): The text to convert to speech.
        Returns:
            bytes: bytes of the audio.
        """
        payload = {
            "model": self.name,
            "voice": self.voice,
            "input": text,
            "stream": True,
        }

        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

            audio_bytes = io.BytesIO()
            for chunk in response.iter_bytes():
                if chunk:
                    yield chunk
                    audio_bytes.write(chunk)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Text-to-Speech streaming failed: {e}")

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(self, text: str) -> AsyncIterator[bytes]:
        """
        Asynchronously streams TTS audio using httpx.

        Parameters:
            text (str): The text to convert to speech.
        Returns:
            io.BytesIO: bytes of the audio.
        """
        payload = {
            "model": self.name,
            "voice": self.voice,
            "input": text,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()
                audio_bytes = io.BytesIO()

                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk
                        audio_bytes.write(chunk)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Text-to-Speech streaming failed: {e}")

    def batch(
        self,
        text_path_dict: Dict[str, str],
    ) -> List[str]:
        """
        Synchronously process multiple text-to-speech requests in batch mode.

        Args:
            text_path_dict (Dict[str, str]): Dictionary mapping text to output paths.

        Returns:
            List[str]: List of paths to the saved audio files.
        """
        return [
            self.predict(text=text, audio_path=path)
            for text, path in text_path_dict.items()
        ]

    async def abatch(
        self,
        text_path_dict: Dict[str, str],
        max_concurrent=5,  # New parameter to control concurrency
    ) -> List[str]:
        """
        Asynchronously process multiple text-to-speech requests in batch mode
        with controlled concurrency.

        Args:
            text_path_dict (Dict[str, str]): Dictionary mapping text to output paths.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[str]: List of paths to the saved audio files.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(text, path) -> str:
            async with semaphore:
                return await self.apredict(text=text, audio_path=path)

        tasks = [
            process_conversation(text, path) for text, path in text_path_dict.items()
        ]
        return await asyncio.gather(*tasks)
