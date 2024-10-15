import io
from typing import List, Literal
from openai import OpenAI
from swarmauri.llms.base.LLMBase import LLMBase

class OpenAIAudioTTS(LLMBase):
    """
    https://platform.openai.com/docs/guides/text-to-speech/overview
    """

    api_key: str
    allowed_models: List[str] = ["tts-1", "tts-1-hd"]

    allowed_voices: List[str] = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    name: str = "tts-1"
    type: Literal["OpenAIAudioTTS"] = "OpenAIAudioTTS"
    voice_name: str = "alloy"

    def predict(self, text: str) -> io.BytesIO:
        """
        Convert text to speech using OpenAI's TTS API and save as an audio file.

        Parameters:
            text (str): The text to convert to speech.
        Returns:
                str: Absolute path to the saved audio file.
        """

        client = OpenAI(api_key=self.api_key)

        try:
            response = client.audio.speech.create(
                model=self.name, voice=self.voice_name, input=text
            )

            audio_bytes = io.BytesIO()

            for chunk in response.iter_bytes(chunk_size=1024):
                if chunk:
                    audio_bytes.write(chunk)

            return audio_bytes
        except Exception as e:
            raise RuntimeError(f"Text-to-Speech synthesis failed: {e}")
