import asyncio
from typing import Dict, List, Literal
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.llms.LLMBase import LLMBase
import httpx
import aiofiles


class GroqAIAudio(LLMBase):
    """
    GroqAIAudio is a class that provides transcription and translation capabilities
    using Groq's audio models. It supports both synchronous and asynchronous methods
    for processing audio files.

    Attributes:
        api_key (str): API key for authentication.
        allowed_models (List[str]): List of supported model names.
        name (str): The default model name to be used for predictions.
        type (Literal["GroqAIAudio"]): The type identifier for the class.
    """

    api_key: str
    allowed_models: List[str] = [
        "distil-whisper-large-v3-en",
        "whisper-large-v3",
    ]

    name: str = "distil-whisper-large-v3-en"
    type: Literal["GroqAIAudio"] = "GroqAIAudio"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.groq.com/openai/v1/audio/")

    def __init__(self, **data):
        """
        Initialize the GroqAIAudio class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )
        self._async_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        """
        Perform synchronous transcription or translation on the provided audio file.

        Args:
            audio_path (str): Path to the audio file.
            task (Literal["transcription", "translation"]): Task type. Defaults to "transcription".

        Returns:
            str: The resulting transcription or translation text.

        Raises:
            ValueError: If the specified task is not supported.
            httpx.HTTPStatusError: If the API request fails.
        """
        kwargs = {
            "model": self.name,
        }

        if task == "translation":
            kwargs["model"] = "whisper-large-v3"

        with open(audio_path, "rb") as audio_file:
            actions = {
                "transcription": self._client.post(
                    "transcriptions", files={"file": audio_file}, data=kwargs
                ),
                "translation": self._client.post(
                    "translations", files={"file": audio_file}, data=kwargs
                ),
            }

            if task not in actions:
                raise ValueError(
                    f"Task {task} not supported. Choose from {list(actions)}"
                )

        response = actions[task]
        response.raise_for_status()

        response_data = response.json()

        return response_data["text"]

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        """
        Perform asynchronous transcription or translation on the provided audio file.

        Args:
            audio_path (str): Path to the audio file.
            task (Literal["transcription", "translation"]): Task type. Defaults to "transcription".

        Returns:
            str: The resulting transcription or translation text.

        Raises:
            ValueError: If the specified task is not supported.
            httpx.HTTPStatusError: If the API request fails.
        """
        kwargs = {
            "model": self.name,
        }
        if task == "translation":
            kwargs["model"] = "whisper-large-v3"

        async with aiofiles.open(audio_path, "rb") as audio_file:
            file_content = await audio_file.read()
            file_name = audio_path.split("/")[-1]
            actions = {
                "transcription": await self._async_client.post(
                    "transcriptions",
                    files={"file": (file_name, file_content, "audio/wav")},
                    data=kwargs,
                ),
                "translation": await self._async_client.post(
                    "translations",
                    files={"file": (file_name, file_content, "audio/wav")},
                    data=kwargs,
                ),
            }
            if task not in actions:
                raise ValueError(
                    f"Task {task} not supported. Choose from {list(actions)}"
                )

            response = actions[task]
            response.raise_for_status()

            response_data = response.json()
            return response_data["text"]

    def batch(
        self,
        path_task_dict: Dict[str, Literal["transcription", "translation"]],
    ) -> List:
        """
        Synchronously process multiple audio files for transcription or translation.

        Args:
            path_task_dict (Dict[str, Literal["transcription", "translation"]]): A dictionary where
                the keys are paths to audio files and the values are the tasks.

        Returns:
            List: A list of resulting texts from each audio file.
        """
        return [
            self.predict(audio_path=path, task=task)
            for path, task in path_task_dict.items()
        ]

    async def abatch(
        self,
        path_task_dict: Dict[str, Literal["transcription", "translation"]],
        max_concurrent=5,
    ) -> List:
        """
        Asynchronously process multiple audio files for transcription or translation
        with controlled concurrency.

        Args:
            path_task_dict (Dict[str, Literal["transcription", "translation"]]): A dictionary where
                the keys are paths to audio files and the values are the tasks.
            max_concurrent (int): Maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List: A list of resulting texts from each audio file.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(path, task) -> str:
            async with semaphore:
                return await self.apredict(audio_path=path, task=task)

        tasks = [
            process_conversation(path, task) for path, task in path_task_dict.items()
        ]
        return await asyncio.gather(*tasks)
