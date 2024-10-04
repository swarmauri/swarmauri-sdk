from typing import List, Literal
from groq import Groq
from swarmauri.llms.base.LLMBase import LLMBase


class GroqAIAudio(LLMBase):
    """
    Groq Audio Model for transcription and translation tasks.
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
