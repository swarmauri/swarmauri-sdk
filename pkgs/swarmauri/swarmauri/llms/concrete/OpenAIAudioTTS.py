from typing import List, Literal
from openai import OpenAI
from swarmauri.llms.base.LLMBase import LLMBase
import os


class OpenAIAudioTTS(LLMBase):
    """
    https://platform.openai.com/docs/api-reference/audio/createTranscription
    """

    api_key: str
    allowed_models: List[str] = ["tts-1", "tts-1-hd"]

    allowed_voices: List[str] = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    name: str = "tts-1"
    type: Literal["OpenAIAudioTTS"] = "OpenAIAudioTTS"
    voice_name: str = "alloy"

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        """
        Convert text to speech using OpenAI's TTS API and save as an audio file.

        Parameters:
            text (str): The text to convert to speech.
            audio_path (str): Path to save the synthesized audio.
        Returns:
                str: Absolute path to the saved audio file.
        """
        client = OpenAI(api_key=self.api_key)

        try:
            response = client.audio.speech.create(
                model=self.name, voice=self.voice_name, input=text
            )
            response.stream_to_file(audio_path)
            return os.path.abspath(audio_path)
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")
