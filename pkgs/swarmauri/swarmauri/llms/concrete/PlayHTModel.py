import asyncio
import io
import json
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

    allowed_models: List[str] = Field(
        default=["Play3.0-mini", "PlayHT2.0-turbo", "PlayHT1.0", "PlayHT2.0"]
    )

    allowed_voices: Dict[
        Literal["Play3.0-mini", "PlayHT2.0-turbo", "PlayHT1.0", "PlayHT2.0"], List[str]
    ] = Field(default_factory=dict)

    voice: str = (
        "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json"
    )

    api_key: str
    user_id: str
    name: str = "Play3.0-mini"
    type: Literal["PlayHTModel"] = "PlayHTModel"
    output_format: str = "mp3"
    base_url: str = "https://api.play.ht/api/v2"

    def __init__(self, **data):
        super().__init__(**data)
        self.allowed_voices = self._fetch_allowed_voices()
        self._validate_voice_in_allowed_voices()

    def _validate_voice_in_allowed_voices(self):
        voice = self.voice
        model = self.name

        if model in self.allowed_models:
            allowed_voices = self.allowed_voices.get(model, [])
            allowed_voices.extend(self.allowed_voices.get("PlayHT2.0"))
        else:
            raise ValueError(
                f"{model} voice engine not allowed. Choose from {self.allowed_models}"
            )
        if voice and voice not in allowed_voices:
            raise ValueError(
                f"Voice name {voice} is not allowed for this {model} voice engine. Choose from {allowed_voices}"
            )

    def _fetch_allowed_voices(self) -> Dict[str, List[str]]:
        """
        Fetch the allowed voices from Play.ht's API and return the dictionary.
        """
        url = f"{self.base_url}/voices"
        headers = {
            "accept": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }
        voice_response = requests.get(url, headers=headers)
        allowed_voices = {}

        for item in json.loads(voice_response.text):
            voice_engine = item.get("voice_engine")
            if voice_engine in self.allowed_models:
                if voice_engine not in allowed_voices:
                    allowed_voices[voice_engine] = [item.get("id")]
                allowed_voices[voice_engine].append(item.get("id"))

        cloned_voice_response = self.get_cloned_voices()
        if cloned_voice_response:
            for item in cloned_voice_response:
                allowed_voices["PlayHT2.0"].append(item.get("id"))

        return allowed_voices

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
            response = requests.post(
                f"{self.base_url}/tts/stream", json=payload, headers=headers
            )
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
                    f"{self.base_url}/tts/stream", json=payload, headers=headers
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
                f"{self.base_url}/tts/stream",
                json=payload,
                headers=headers,
                stream=True,
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
                    f"{self.base_url}/tts/stream", json=payload, headers=headers
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

    def clone_voice_from_file(self, voice_name: str, sample_file_path: str) -> dict:
        """
        Clone a voice by sending a sample audio file to Play.ht API.

        :param voice_name: The name for the cloned voice.
        :param sample_file_path: The path to the audio file to be used for cloning the voice.
        :return: A dictionary containing the response from the Play.ht API.
        """
        url = f"{self.base_url}/cloned-voices/instant"

        files = {
            "sample_file": (
                sample_file_path.split("/")[-1],
                open(sample_file_path, "rb"),
                "audio/mp4",
            )
        }
        payload = {"voice_name": voice_name}

        headers = {
            "accept": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            response = requests.post(url, data=payload, files=files, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while cloning the voice: {e}")
            return {"error": str(e)}

    def clone_voice_from_url(self, voice_name: str, sample_file_url: str) -> dict:
        """
        Clone a voice by sending a URL to an audio file to Play.ht API.

        :param voice_name: The name for the cloned voice.
        :param sample_file_url: The URL to the audio file to be used for cloning the voice.
        :return: A dictionary containing the response from the Play.ht API.
        """
        url = f"{self.base_url}/cloned-voices/instant"

        # Constructing the payload with the sample file URL
        payload = f'-----011000010111000001101001\r\nContent-Disposition: form-data; name="sample_file_url"\r\n\r\n{sample_file_url}\r\n-----011000010111000001101001--; name="voice_name"\r\n\r\n{voice_name}\r\n-----011000010111000001101001--'

        headers = {
            "accept": "application/json",
            "content-type": "multipart/form-data; boundary=---011000010111000001101001",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while cloning the voice: {e}")
            return {"error": str(e)}

    def delete_cloned_voice(self, voice_id: str) -> dict:
        """
        Delete a cloned voice using its voice_id from Play.ht.

        :param voice_id: The ID of the cloned voice to delete.
        :return: A dictionary containing the response from the Play.ht API.
        """
        url = f"{self.base_url}/cloned-voices/"

        payload = {"voice_id": voice_id}

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            response = requests.delete(url, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while deleting the cloned voice: {e}")
            return {"error": str(e)}

    def get_cloned_voices(self) -> dict:
        """
        Get a list of cloned voices from Play.ht.

        :return: A dictionary containing the cloned voices or an error message.
        """
        url = f"{self.base_url}/cloned-voices"

        headers = {
            "accept": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while retrieving cloned voices: {e}")
            return {"error": str(e)}
