from typing import List, Literal
from openai import OpenAI
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
