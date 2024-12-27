import asyncio
import json
import os

import httpx
from typing import List, Literal, Dict

from pydantic import Field, PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.llms.LLMBase import LLMBase


class PlayHTModel(LLMBase):
    """
    A class for Play.ht text-to-speech (TTS) synthesis using various voice models.

    This class interacts with the Play.ht API to synthesize text to speech,
    clone voices, and manage voice operations (like getting, cloning, and deleting).
    Attributes:
        allowed_models (List[str]): List of TTS models supported by Play.ht, such as "Play3.0-mini" and "PlayHT2.0".
        allowed_voices (List[str]): List of voice names available for the selected model.
        voice (str): The selected voice name for synthesis (default: "Adolfo").
        api_key (str): API key for authenticating with Play.ht's API.
        user_id (str): User ID for authenticating with Play.ht's API.
        name (str): Name of the TTS model to use (default: "Play3.0-mini").
        type (Literal["PlayHTModel"]): Fixed type attribute to indicate this is a "PlayHTModel".
        output_format (str): Format of the output audio file, e.g., "mp3".

    Provider resourses: https://docs.play.ht/reference/api-getting-started
    """

    allowed_models: List[str] = Field(
        default=["Play3.0-mini", "PlayHT2.0-turbo", "PlayHT1.0", "PlayHT2.0"]
    )
    allowed_voices: List[str] = Field(default=None)
    voice: str = Field(default="Adolfo")
    api_key: str
    user_id: str
    name: str = "Play3.0-mini"
    type: Literal["PlayHTModel"] = "PlayHTModel"
    output_format: str = "mp3"
    _voice_id: str = PrivateAttr(default=None)
    _prebuilt_voices: Dict[
        Literal["Play3.0-mini", "PlayHT2.0-turbo", "PlayHT1.0", "PlayHT2.0"], List[dict]
    ] = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.play.ht/api/v2")
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data) -> None:
        """
        Initialize the PlayHTModel with API credentials and voice settings.
        """
        super().__init__(**data)
        self._headers = {
            "accept": "audio/mpeg",
            "content-type": "application/json",
            "AUTHORIZATION": self.api_key,
            "X-USER-ID": self.user_id,
        }
        self.__prebuilt_voices = self._fetch_prebuilt_voices()
        self.allowed_voices = self._get_allowed_voices(self.name)
        self._validate_voice_in_allowed_voices()

    def _validate_voice_in_allowed_voices(self) -> None:
        """
        Validate the voice name against the allowed voices for the model.
        """
        voice = self.voice
        model = self.name

        if model not in self.allowed_models:
            raise ValueError(
                f"{model} voice engine not allowed. Choose from {self.allowed_models}"
            )
        if voice and voice not in self.allowed_voices:
            raise ValueError(
                f"Voice name {voice} is not allowed for this {model} voice engine. Choose from {self.allowed_voices}"
            )

    @retry_on_status_codes((429, 529), max_retries=1)
    def _fetch_prebuilt_voices(self) -> Dict[str, List[str]]:
        """
        Fetch prebuilt voices for each allowed model from the Play.ht API.

        Returns:
            dict: Dictionary mapping models to lists of voice dictionaries.
        """
        prebuilt_voices = {}

        self._headers["accept"] = "application/json"

        with httpx.Client(base_url=self._BASE_URL, timeout=30) as client:
            voice_response = client.get("/voices", headers=self._headers)

        for item in json.loads(voice_response.text):
            voice_engine = item.get("voice_engine")
            if voice_engine in self.allowed_models:
                if voice_engine not in prebuilt_voices:
                    prebuilt_voices[voice_engine] = []
            prebuilt_voices[voice_engine].append({item.get("id"): item.get("name")})

        cloned_voice_response = self.get_cloned_voices()
        if cloned_voice_response:
            for item in cloned_voice_response:
                prebuilt_voices["PlayHT2.0"].append({item.get("id"): item.get("name")})

        return prebuilt_voices

    def _get_allowed_voices(self, model: str) -> List[str]:
        """
        Retrieve allowed voices for a specified model.

        Parameters:
            model (str): The model name to retrieve voices for.

        Returns:
            list: List of allowed voice names.
        """
        allowed_voices = []

        if model in self.allowed_models:
            for item in self.__prebuilt_voices.get(model, []):
                allowed_voices.append(*item.values())
            if model != "PlayHT2.0":
                allowed_voices.extend(self._get_allowed_voices("PlayHT2.0"))
        return allowed_voices

    def _get_voice_id(self, voice_name: str) -> str:
        """
        Retrieve the voice ID associated with a given voice name.

        Parameters:
            voice_name (str): The name of the voice to retrieve the ID for.

        Returns:
            str: Voice ID for the specified voice name.
        """
        if self.name in self.allowed_models:
            for item in self.__prebuilt_voices.get(
                self.name, self.__prebuilt_voices.get("PlayHT2.0")
            ):
                if voice_name in item.values():
                    return list(item.keys())[0]

        raise ValueError(f"Voice name {voice_name} not found in allowed voices.")

    @retry_on_status_codes((429, 529), max_retries=1)
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
            "voice": self._get_voice_id(self.voice),
            "output_format": self.output_format,
            "voice_engine": self.name,
            "text": text,
        }

        try:
            with httpx.Client(base_url=self._BASE_URL, timeout=30) as self._client:
                response = self._client.post(
                    "/tts/stream", json=payload, headers=self._headers
                )
                response.raise_for_status()

            with open(audio_path, "wb") as f:
                f.write(response.content)

            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Asynchronously convert text to speech and save it as an audio file.

        Parameters:
            text (str): Text to convert to speech.
            audio_path (str): Path to save the synthesized audio file.

        Returns:
            str: Path to the saved audio file.
        """
        payload = {
            "voice": self._get_voice_id(self.voice),
            "output_format": self.output_format,
            "voice_engine": self.name,
            "text": text,
        }

        try:
            async with httpx.AsyncClient(
                base_url=self._BASE_URL, timeout=30
            ) as async_client:
                response = await async_client.post(
                    "/tts/stream", json=payload, headers=self._headers
                )
                response.raise_for_status()
            with open(audio_path, "wb") as f:
                f.write(response.content)
            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")

    def batch(self, text_path_dict: Dict[str, str]) -> List:
        """
        Process multiple text-to-speech conversions synchronously.

        Parameters:
            text_path_dict (Dict[str, str]): Dictionary of text and corresponding audio paths.
        Returns:
            List: List of audio file paths.
        """
        return [self.predict(text, path) for text, path in text_path_dict.items()]

    async def abatch(
        self, text_path_dict: Dict[str, str], max_concurrent: int = 5
    ) -> List["str"]:
        """
        Process multiple text-to-speech conversions asynchronously with controlled concurrency.

        Parameters:
            text_path_dict (Dict[str, str]): Dictionary of text and corresponding audio paths.
            max_concurrent (int): Maximum number of concurrent tasks.
        Returns:
            List: List of audio file paths.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_text(text, path) -> str:
            async with semaphore:
                return await self.apredict(text, path)

        tasks = [process_text(text, path) for text, path in text_path_dict.items()]
        return await asyncio.gather(*tasks)

    def clone_voice_from_file(self, voice_name: str, sample_file_path: str) -> dict:
        """
        Clone a voice using an audio file.

        Parameters:
            voice_name (str): The name for the cloned voice.
            sample_file_path (str): Path to the sample audio file.

        Returns:
            dict: Response from the Play.ht API.
        """
        files = {
            "sample_file": (
                sample_file_path.split("/")[-1],
                open(sample_file_path, "rb"),
                "audio/mp4",
            )
        }
        payload = {"voice_name": voice_name}
        self._headers["accept"] = "application/json"

        try:
            with httpx.Client(base_url=self._BASE_URL) as client:
                response = client.post(
                    "/cloned-voices/instant",
                    data=payload,
                    files=files,
                    headers=self._headers,
                )
                response.raise_for_status()

            return response.json()
        except httpx.RequestError as e:
            print(f"An error occurred while cloning the voice: {e}")
            return {"error": str(e)}

    def clone_voice_from_url(self, voice_name: str, sample_file_url: str) -> dict:
        """
        Clone a voice by sending a URL to an audio file to Play.ht API.

        :param voice_name: The name for the cloned voice.
        :param sample_file_url: The URL to the audio file to be used for cloning the voice.
        :return: A dictionary containing the response from the Play.ht API.
        """
        # Constructing the payload with the sample file URL
        payload = f'-----011000010111000001101001\r\nContent-Disposition: form-data; name="sample_file_url"\r\n\r\n\
            {sample_file_url}\r\n-----011000010111000001101001--; name="voice_name"\r\n\r\n\
            {voice_name}\r\n-----011000010111000001101001--'

        self._headers["content-type"] = (
            "multipart/form-data; boundary=---011000010111000001101001"
        )
        self._headers["accept"] = "application/json"

        try:
            with httpx.Client(base_url=self._BASE_URL) as client:
                response = client.post(
                    "/cloned-voices/instant", data=payload, headers=self._headers
                )
                response.raise_for_status()

            return response.json()

        except httpx.RequestError as e:
            print(f"An error occurred while cloning the voice: {e}")
            return {"error": str(e)}

    def delete_cloned_voice(self, voice_id: str) -> dict:
        """
        Delete a cloned voice using its voice_id from Play.ht.

        :param voice_id: The ID of the cloned voice to delete.
        :return: A dictionary containing the response from the Play.ht API.
        """

        payload = {"voice_id": voice_id}
        self._headers["accept"] = "application/json"

        try:
            with httpx.Client(base_url=self._BASE_URL) as client:
                response = client.delete(
                    "/cloned-voices", json=payload, headers=self._headers
                )
                response.raise_for_status()

            return response.json()

        except httpx.RequestError as e:
            print(f"An error occurred while deleting the cloned voice: {e}")
            return {"error": str(e)}

    def get_cloned_voices(self) -> dict:
        """
        Get a list of cloned voices from Play.ht.

        :return: A dictionary containing the cloned voices or an error message.
        """
        self._headers["accept"] = "application/json"

        try:
            with httpx.Client(base_url=self._BASE_URL) as client:
                response = client.get("/cloned-voices", headers=self._headers)
                response.raise_for_status()

            return response.json()

        except httpx.RequestError as e:
            print(f"An error occurred while retrieving cloned voices: {e}")
            return {"error": str(e)}
