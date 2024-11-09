from typing import List, Literal, Dict
import requests
import asyncio
import aiohttp
from swarmauri.llms.base.LLMBase import LLMBase


class WhisperLargeModel(LLMBase):
    """
    Implementation of Whisper Large V3 model using HuggingFace's Inference API
    https://huggingface.co/openai/whisper-large-v3
    """

    allowed_models: List[str] = ["openai/whisper-large-v3"]
    name: str = "openai/whisper-large-v3"
    type: Literal["WhisperLargeModel"] = "WhisperLargeModel"
    api_key: str

    __API_URL: str = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"

    def predict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        """
        Process a single audio file using the Hugging Face Inference API

        Args:
            audio_path (str): Path to the audio file
            task (Literal["transcription", "translation"]): Task to perform

        Returns:
            str: Transcribed or translated text
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}

        if task not in ["transcription", "translation"]:
            raise ValueError(
                f"Task {task} not supported. Choose from ['transcription', 'translation']"
            )

        with open(audio_path, "rb") as audio_file:
            data = audio_file.read()

        params = {"task": task}
        if task == "translation":
            params["language"] = "en"

        response = requests.post(
            self.__API_URL, headers=headers, data=data, params=params
        )

        if response.status_code != 200:
            raise Exception(
                f"API request failed with status code {response.status_code}: {response.text}"
            )

        result = response.json()

        if isinstance(result, dict):
            return result.get("text", "")
        elif isinstance(result, list) and len(result) > 0:
            return result[0].get("text", "")
        else:
            raise Exception("Unexpected API response format")

    async def apredict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        """
        Asynchronously process a single audio file
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}

        if task not in ["transcription", "translation"]:
            raise ValueError(
                f"Task {task} not supported. Choose from ['transcription', 'translation']"
            )

        with open(audio_path, "rb") as audio_file:
            data = audio_file.read()

        params = {"task": task}
        if task == "translation":
            params["language"] = "en"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.__API_URL, headers=headers, data=data, params=params
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"API request failed with status code {response.status}: {await response.text()}"
                    )

                result = await response.json()

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
        Synchronously process multiple audio files
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
        Process multiple audio files in parallel with controlled concurrency

        Args:
            path_task_dict (Dict[str, Literal["transcription", "translation"]]):
                Dictionary mapping file paths to tasks
            max_concurrent (int): Maximum number of concurrent requests

        Returns:
            List[str]: List of transcribed/translated texts
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_audio(path: str, task: str) -> str:
            async with semaphore:
                return await self.apredict(audio_path=path, task=task)

        tasks = [process_audio(path, task) for path, task in path_task_dict.items()]

        return await asyncio.gather(*tasks)
