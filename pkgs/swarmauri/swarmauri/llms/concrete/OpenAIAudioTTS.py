import asyncio
import io
import os
from typing import List, Literal, Dict
from openai import OpenAI, AsyncOpenAI
from pydantic import model_validator
from swarmauri.llms.base.LLMBase import LLMBase


class OpenAIAudioTTS(LLMBase):
    """
    https://platform.openai.com/docs/guides/text-to-speech/overview
    """

    api_key: str
    allowed_models: List[str] = ["tts-1", "tts-1-hd"]

    allowed_voices: List[str] = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    name: str = "tts-1"
    type: Literal["OpenAIAudioTTS"] = "OpenAIAudioTTS"
    voice: str = "alloy"

    @model_validator(mode="after")
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        voice = values.voice
        allowed_voices = values.allowed_voices
        if voice and voice not in allowed_voices:
            raise ValueError(
                f"Model name {voice} is not allowed. Choose from {allowed_voices}"
            )
        return values

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Convert text to speech using OpenAI's TTS API and save as an audio file.

        Parameters:
            text (str): The text to convert to speech.
            audio_path (str): Path to save the synthesized audio.
        Returns:
                str: Absolute path to the saved audio file.
        """
        client = OpenAI(api_key=self.api_key)

        try:
            response = client.audio.speech.create(
                model=self.name, voice=self.voice, input=text
            )
            response.stream_to_file(audio_path)
            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Asychronously converts text to speech using OpenAI's TTS API and save as an audio file.

        Parameters:
            text (str): The text to convert to speech.
            audio_path (str): Path to save the synthesized audio.
        Returns:
                str: Absolute path to the saved audio file.
        """
        async_client = AsyncOpenAI(api_key=self.api_key)

        try:
            response = await async_client.audio.speech.create(
                model=self.name, voice=self.voice, input=text
            )
            await response.astream_to_file(audio_path)
            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    def stream(self, text: str) -> bytes:
        """
        Convert text to speech using OpenAI's TTS API.

        Parameters:
            text (str): The text to convert to speech.
        Returns:
                bytes: bytes of the audio.
        """

        client = OpenAI(api_key=self.api_key)

        try:
            response = client.audio.speech.create(
                model=self.name, voice=self.voice, input=text
            )

            audio_bytes = io.BytesIO()

            for chunk in response.iter_bytes(chunk_size=1024):
                if chunk:
                    yield chunk
                    audio_bytes.write(chunk)

        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    async def astream(self, text: str) -> io.BytesIO:
        """
        Convert text to speech using OpenAI's TTS API.

        Parameters:
            text (str): The text to convert to speech.
        Returns:
                bytes: bytes of the audio.
        """

        async_client = AsyncOpenAI(api_key=self.api_key)

        try:
            response = await async_client.audio.speech.create(
                model=self.name, voice=self.voice, input=text
            )

            audio_bytes = io.BytesIO()

            async for chunk in await response.aiter_bytes(chunk_size=1024):
                if chunk:
                    yield chunk
                    audio_bytes.write(chunk)

        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    def batch(
        self,
        text_path_dict: Dict[str, str],
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(text=text, audio_path=path)
            for text, path in text_path_dict.items()
        ]

    async def abatch(
        self,
        text_path_dict: Dict[str, str],
        max_concurrent=5,  # New parameter to control concurrency
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(text, path):
            async with semaphore:
                return await self.apredict(text=text, audio_path=path)

        tasks = [
            process_conversation(text, path) for text, path in text_path_dict.items()
        ]
        return await asyncio.gather(*tasks)
