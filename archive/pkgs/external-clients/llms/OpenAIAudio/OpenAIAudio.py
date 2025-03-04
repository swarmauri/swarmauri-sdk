import asyncio
from typing import List, Literal, Dict
from openai import OpenAI, AsyncOpenAI
from swarmauri.llms.base.LLMBase import LLMBase


class OpenAIAudio(LLMBase):
    """
    https://platform.openai.com/docs/api-reference/audio/createTranscription
    """

    api_key: str
    allowed_models: List[str] = ["whisper-1"]

    name: str = "whisper-1"
    type: Literal["OpenAIAudio"] = "OpenAIAudio"

    def predict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        client = OpenAI(api_key=self.api_key)
        actions = {
            "transcription": client.audio.transcriptions,
            "translation": client.audio.translations,
        }

        if task not in actions:
            raise ValueError(f"Task {task} not supported. Choose from {list(actions)}")

        kwargs = {
            "model": self.name,
        }

        with open(audio_path, "rb") as audio_file:
            response = actions[task].create(**kwargs, file=audio_file)

        return response.text

    async def apredict(
        self,
        audio_path: str,
        task: Literal["transcription", "translation"] = "transcription",
    ) -> str:
        async_client = AsyncOpenAI(api_key=self.api_key)

        actions = {
            "transcription": async_client.audio.transcriptions,
            "translation": async_client.audio.translations,
        }

        if task not in actions:
            raise ValueError(f"Task {task} not supported. Choose from {list(actions)}")

        kwargs = {
            "model": self.name,
        }

        with open(audio_path, "rb") as audio_file:
            response = await actions[task].create(**kwargs, file=audio_file)

        return response.text

    def batch(
        self,
        path_task_dict: Dict[str, Literal["transcription", "translation"]],
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(audio_path=path, task=task)
            for path, task in path_task_dict.items()
        ]

    async def abatch(
        self,
        path_task_dict: Dict[str, Literal["transcription", "translation"]],
        max_concurrent=5,  # New parameter to control concurrency
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(path, task):
            async with semaphore:
                return await self.apredict(audio_path=path, task=task)

        tasks = [
            process_conversation(path, task) for path, task in path_task_dict.items()
        ]
        return await asyncio.gather(*tasks)
