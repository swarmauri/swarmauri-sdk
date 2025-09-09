import asyncio
from typing import Any, Dict, List, Literal

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.stt.STTBase import STTBase
from swarmauri_base.ComponentBase import ComponentBase

from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(STTBase, "WhisperLargeSTT")
class WhisperLargeSTT(STTBase):
    """
    A class implementing OpenAI's Whisper Large V3 model using HuggingFace's Inference API.

    This class provides both synchronous and asynchronous methods for transcribing or
    translating audio files using the Whisper Large V3 model. It supports both single
    file processing and batch processing with controlled concurrency.

    Attributes:
        allowed_models (List[str]): List of supported model identifiers.
        name (str): The name/identifier of the model being used.
        type (Literal["WhisperLargeSTT"]): Type identifier for the model.
        api_key (str): HuggingFace API key for authentication.

    Link to API KEY: https://huggingface.co/login?next=%2Fsettings%2Ftokens

    Example:
        >>> model = WhisperLargeSTT(api_key="your-api-key")
        >>> text = model.predict("audio.mp3", task="transcription")
        >>> print(text)
    """

    allowed_models: List[str] = ["openai/whisper-large-v3"]
    name: str = "openai/whisper-large-v3"
    type: Literal["WhisperLargeSTT"] = "WhisperLargeSTT"
    api_key: SecretStr
    _BASE_URL: str = PrivateAttr(
        "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    )
    _client: httpx.Client = PrivateAttr()
    _header: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data: Dict[str, Any]):
        """
        Initialize the WhisperLargeSTT instance.

        Args:
            **data (Dict[str, Any]): Keyword arguments containing model configuration.
                   Must include 'api_key' for HuggingFace API authentication.

        Raises:
            ValueError: If required configuration parameters are missing.
        """
        super().__init__(**data)
        self._header = {"Authorization": f"Bearer {self.api_key.get_secret_value()}"}
        self._client = httpx.Client(headers=self._header, timeout=30)
        self.allowed_models = self.allowed_models or self.get_allowed_models()
        self.name = self.allowed_models[0]

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        """
        Process a single audio file using the Hugging Face Inference API.

        Args:
            audio_path (str): Path to the audio file to be processed.
            task (Literal["transcription", "translation"]): Task to perform.
                'transcription': Transcribe audio in its original language.
                'translation': Translate audio to English.

        Returns:
            str: Transcribed or translated text from the audio file.

        Raises:
            ValueError: If the specified task is not supported.
            Exception: If the API response format is unexpected.
            httpx.HTTPError: If the API request fails.
        """
        if task not in ["transcription", "translation"]:
            raise ValueError(
                f"Task {task} not supported. Choose from ['transcription', 'translation']"
            )

        with open(audio_path, "rb") as audio_file:
            data = audio_file.read()

        params = {"task": task}
        if task == "translation":
            params["language"] = "en"

        response = self._client.post(self._BASE_URL, data=data, params=params)
        response.raise_for_status()
        result = response.json()

        if isinstance(result, dict):
            return result.get("text", "")
        elif isinstance(result, list) and len(result) > 0:
            return result[0].get("text", "")
        else:
            raise Exception("Unexpected API response format")

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        """
        Asynchronously process a single audio file.

        This method provides the same functionality as `predict()` but operates
        asynchronously for better performance in async contexts.

        Args:
            audio_path (str): Path to the audio file to be processed.
            task (Literal["transcription", "translation"]): Task to perform.
                'transcription': Transcribe audio in its original language.
                'translation': Translate audio to English.

        Returns:
            str: Transcribed or translated text from the audio file.

        Raises:
            ValueError: If the specified task is not supported.
            Exception: If the API response format is unexpected.
            httpx.HTTPError: If the API request fails.
        """
        if task not in ["transcription", "translation"]:
            raise ValueError(
                f"Task {task} not supported. Choose from ['transcription', 'translation']"
            )

        with open(audio_path, "rb") as audio_file:
            data = audio_file.read()

        params = {"task": task}
        if task == "translation":
            params["language"] = "en"

        async with httpx.AsyncClient(headers=self._header) as client:
            response = await client.post(self._BASE_URL, data=data, params=params)
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict):
                return result.get("text", "")
            elif isinstance(result, list) and len(result) > 0:
                return result[0].get("text", "")
            else:
                raise Exception("Unexpected API response format")

    def batch(
        self,
        path_task_dict: Dict[str, Literal["transcription", "translation"]],
    ) -> List[str]:
        """
        Synchronously process multiple audio files.

        Args:
            path_task_dict (Dict[str, Literal["transcription", "translation"]]):
                Dictionary mapping file paths to their respective tasks.
                Key: Path to audio file.
                Value: Task to perform ("transcription" or "translation").

        Returns:
            List[str]: List of processed texts, maintaining the order of input files.

        Example:
            >>> files = {
            ...     "file1.mp3": "transcription",
            ...     "file2.mp3": "translation"
            ... }
            >>> results = model.batch(files)
        """
        return [
            self.predict(audio_path=path, task=task)
            for path, task in path_task_dict.items()
        ]

    async def abatch(
        self,
        path_task_dict: Dict[str, Literal["transcription", "translation"]],
        max_concurrent: int = 5,
    ) -> List[str]:
        """
        Process multiple audio files in parallel with controlled concurrency.

        This method provides the same functionality as `batch()` but operates
        asynchronously with controlled concurrency to prevent overwhelming
        the API or local resources.

        Args:
            path_task_dict (Dict[str, Literal["transcription", "translation"]]):
                Dictionary mapping file paths to their respective tasks.
                Key: Path to audio file.
                Value: Task to perform ("transcription" or "translation").
            max_concurrent (int, optional): Maximum number of concurrent requests.
                Defaults to 5.

        Returns:
            List[str]: List of processed texts, maintaining the order of input files.

        Example:
            >>> files = {
            ...     "file1.mp3": "transcription",
            ...     "file2.mp3": "translation"
            ... }
            >>> results = await model.abatch(files, max_concurrent=3)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_audio(path: str, task: str) -> str:
            async with semaphore:
                return await self.apredict(audio_path=path, task=task)

        tasks = [process_audio(path, task) for path, task in path_task_dict.items()]
        return await asyncio.gather(*tasks)

    def get_allowed_models(self) -> List[str]:
        """
        Queries the LLMProvider API endpoint to retrieve the list of allowed models.

        Returns:
            List[str]: List of allowed model names.
        """
        models_data = ["openai/whisper-large-v3"]
        return models_data

    def stream(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        raise NotImplementedError(
            "Stream method is not implemented for WhisperLargeSTT"
        )

    async def astream(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        raise NotImplementedError(
            "Stream method is not implemented for WhisperLargeSTT"
        )
