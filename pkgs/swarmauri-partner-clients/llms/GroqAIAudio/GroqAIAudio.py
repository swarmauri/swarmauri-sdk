import asyncio
from typing import Dict, List, Literal
from groq import Groq, AsyncGroq
from swarmauri.llms.base.LLMBase import LLMBase


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
        client = Groq(api_key=self.api_key)
        actions = {
            "transcription": client.audio.transcriptions,
            "translation": client.audio.translations,
        }

        if task not in actions:
            raise ValueError(f"Task {task} not supported. Choose from {list(actions)}")

        kwargs = {
            "model": self.name,
        }

        if task == "translation":
            kwargs["model"] = "whisper-large-v3"

        with open(audio_path, "rb") as audio_file:
            response = actions[task].create(**kwargs, file=audio_file)

        return response.text

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
        async_client = AsyncGroq(api_key=self.api_key)

        actions = {
            "transcription": async_client.audio.transcriptions,
            "translation": async_client.audio.translations,
        }

        if task not in actions:
            raise ValueError(f"Task {task} not supported. Choose from {list(actions)}")

        kwargs = {
            "model": self.name,
        }

        if task == "translation":
            kwargs["model"] = "whisper-large-v3"

        with open(audio_path, "rb") as audio_file:
            response = await actions[task].create(**kwargs, file=audio_file)

        return response.text

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
        max_concurrent=5,  # New parameter to control concurrency
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

        async def process_conversation(path, task):
            async with semaphore:
                return await self.apredict(audio_path=path, task=task)

        tasks = [
            process_conversation(path, task) for path, task in path_task_dict.items()
        ]
        return await asyncio.gather(*tasks)