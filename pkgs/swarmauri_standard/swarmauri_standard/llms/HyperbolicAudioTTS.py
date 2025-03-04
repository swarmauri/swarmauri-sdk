import asyncio
import base64
import os
import warnings
from typing import Dict, List, Literal, Optional

import httpx
from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase

warnings.warn(
    "Importing HyperbolicAudioTTS from swarmauri.llms is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_standard.tts import "
    "HyperbolicTTS' or 'from swarmauri.tts import HyperbolicTTS' instead.",
    DeprecationWarning,
    stacklevel=2,
)


@ComponentBase.register_type(LLMBase, "HyperbolicAudioTTS")
class HyperbolicAudioTTS(LLMBase):
    """
    A class to interact with Hyperbolic's Text-to-Speech API, allowing for synchronous
    and asynchronous text-to-speech synthesis.

    Attributes:
        api_key (str): The API key for accessing Hyperbolic's TTS service.
        language (Optional[str]): Language of the text.
        speaker (Optional[str]): Specific speaker variant.
        speed (Optional[float]): Speech speed control.

    Provider Resource: https://api.hyperbolic.xyz/v1/audio/generation
    Link to API KEYS: https://app.hyperbolic.xyz/settings
    """

    api_key: SecretStr

    # Supported languages
    allowed_languages: List[str] = ["EN", "ES", "FR", "ZH", "JP", "KR"]

    # Supported speakers per language
    allowed_speakers: Dict[str, List[str]] = {
        "EN": ["EN-US", "EN-BR", "EN-INDIA", "EN-AU"],
        "ES": ["ES"],
        "FR": ["FR"],
        "ZH": ["ZH"],
        "JP": ["JP"],
        "KR": ["KR"],
    }

    # Optional parameters with type hints and validation
    language: Optional[str] = None
    speaker: Optional[str] = None
    speed: Optional[float] = Field(default=1.0, ge=0.1, le=5)
    timeout: float = 600.0

    type: Literal["HyperbolicAudioTTS"] = "HyperbolicAudioTTS"
    _BASE_URL: str = PrivateAttr(
        default="https://api.hyperbolic.xyz/v1/audio/generation"
    )
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data):
        """
        Initialize the HyperbolicAudioTTS class with the provided data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    def _prepare_payload(self, text: str) -> Dict:
        """
        Prepare the payload for the TTS request.
        """
        payload = {"text": text}

        # Add optional parameters if they are set
        if self.language:
            payload["language"] = self.language
        if self.speaker:
            payload["speaker"] = self.speaker
        if self.speed is not None:
            payload["speed"] = self.speed

        return payload

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Synchronously converts text to speech.
        """
        payload = self._prepare_payload(text)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self._BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()

            # Decode base64 audio
            audio_data = base64.b64decode(response.json()["audio"])

            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio_data)

            return os.path.abspath(audio_path)

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Asynchronously converts text to speech.
        """
        payload = self._prepare_payload(text)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()

            # Decode base64 audio
            audio_data = base64.b64decode(response.json()["audio"])

            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio_data)

            return os.path.abspath(audio_path)

    def batch(
        self,
        text_path_dict: Dict[str, str],
    ) -> List[str]:
        """
        Synchronously process multiple text-to-speech requests in batch mode.
        """
        return [
            self.predict(text=text, audio_path=path)
            for text, path in text_path_dict.items()
        ]

    async def abatch(
        self,
        text_path_dict: Dict[str, str],
        max_concurrent=5,
    ) -> List[str]:
        """
        Asynchronously process multiple text-to-speech requests in batch mode.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(text, path) -> str:
            async with semaphore:
                return await self.apredict(text=text, audio_path=path)

        tasks = [
            process_conversation(text, path) for text, path in text_path_dict.items()
        ]
        return await asyncio.gather(*tasks)

    def stream(
        self,
        text: str,
        audio_path: str = "output.mp3",
    ) -> str:
        """
        Stream the text-to-speech output.
        """
        raise NotImplementedError("Stream method is not implemented for HyperbolicTTS")

    async def astream(
        self,
        text: str,
        audio_path: str = "output.mp3",
    ) -> str:
        """
        Asynchronously stream the text-to-speech output.
        """
        raise NotImplementedError("AStream method is not implemented for HyperbolicTTS")
