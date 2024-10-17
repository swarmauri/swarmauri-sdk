import asyncio
import io
import os

import aiohttp
import requests
from typing import List, Literal, Dict

from pydantic import Field
from swarmauri.llms.base.LLMBase import LLMBase


class PlayHTModel(LLMBase):
    """
    Play.ht TTS class for text-to-speech synthesis
    """

    api_key: str
    user_id: str
    allowed_models: List[str] = Field(default=["Play3.0-mini", "PlayHT2.0-turbo"])
    allowed_voices: List[str] = Field(
        default=[
            "s3://voice-cloning-zero-shot/775ae416-49bb-4fb6-bd45-740f205d20a1/jennifersaad/manifest.json"
        ]
    )
    voice: str = (
        "s3://voice-cloning-zero-shot/775ae416-49bb-4fb6-bd45-740f205d20a1/jennifersaad/manifest.json"
    )
    name: str = "Play3.0-mini"
    output_format: str = "mp3"
    base_url: str = "https://api.play.ht/api/v2/tts/stream"

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Convert text to speech using Play.ht's API and save as an audio file.

        Parameters:
            text (str): The text to convert to speech.
            audio_path (str): Path to save the synthesized audio.
        Returns:
            str: Absolute path to the saved audio file.
        """
        payload = {
            "voice": self.voice,
            "output_format": self.output_format,
            "voice_engine": self.name,
            "text": text,
        }
        headers = {
            "accept": "audio/mpeg",
            "content-type": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()

            with open(audio_path, "wb") as f:
                f.write(response.content)

            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Asynchronously converts text to speech using Play.ht's API and saves as an audio file.
        """
        payload = {
            "voice": self.voice,
            "output_format": self.output_format,
            "voice_engine": self.name,
            "text": text,
        }
        headers = {
            "accept": "audio/mpeg",
            "content-type": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(
                            f"Text-to-Speech synthesis failed: {response.status}"
                        )
                    content = await response.read()
                    with open(audio_path, "wb") as f:
                        f.write(content)
            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    def stream(self, text: str) -> bytes:
        """
        Stream text-to-speech audio from Play.ht's API.

        Parameters:
            text (str): The text to convert to speech.
        Returns:
            Generator: Stream of audio bytes.
        """
        payload = {
            "voice": self.voice,
            "output_format": self.output_format,
            "voice_engine": self.name,
            "text": text,
        }
        headers = {
            "accept": "audio/mpeg",
            "content-type": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, stream=True
            )
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

        except Exception as e:
            raise RuntimeError(f"Text-to-Speech streaming failed: {e}")

    async def astream(self, text: str) -> io.BytesIO:
        """
        Asynchronously stream text-to-speech audio from Play.ht's API.
        """
        payload = {
            "voice": self.voice,
            "output_format": self.output_format,
            "voice_engine": self.name,
            "text": text,
        }
        headers = {
            "accept": "audio/mpeg",
            "content-type": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            audio_bytes = io.BytesIO()
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(
                            f"Text-to-Speech streaming failed: {response.status}"
                        )
                    async for chunk in response.content.iter_chunked(1024):
                        if chunk:
                            audio_bytes.write(chunk)

            return audio_bytes
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech streaming failed: {e}")

    def batch(self, text_path_dict: Dict[str, str]) -> List:
        """
        Process multiple text-to-speech conversions synchronously.

        Parameters:
            text_path_dict (Dict[str, str]): Dictionary of text and corresponding audio paths.
        Returns:
            List: List of audio file paths.
        """
        return [self.predict(text, path) for text, path in text_path_dict.items()]

    async def abatch(self, text_path_dict: Dict[str, str], max_concurrent=5) -> List:
        """
        Process multiple text-to-speech conversions asynchronously with controlled concurrency.

        Parameters:
            text_path_dict (Dict[str, str]): Dictionary of text and corresponding audio paths.
            max_concurrent (int): Maximum number of concurrent tasks.
        Returns:
            List: List of audio file paths.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_text(text, path):
            async with semaphore:
                return await self.apredict(text, path)

        tasks = [process_text(text, path) for text, path in text_path_dict.items()]
        return await asyncio.gather(*tasks)
