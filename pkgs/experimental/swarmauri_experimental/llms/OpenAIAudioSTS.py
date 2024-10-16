from typing import List, Literal, Optional
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.llms.concrete.OpenAIModel import OpenAIModel
from swarmauri.messages.concrete import HumanMessage, SystemMessage

from swarmauri.llms.concrete.OpenAIAudio import OpenAIAudio
from swarmauri.llms.concrete.OpenAIAudioTTS import OpenAIAudioTTS


class OpenAIAudioSTS(LLMBase):
    """
    https://platform.openai.com/docs/api-reference/audio/createTranscription
    """

    api_key: str
    type: Literal["OpenAIAudioSTS"] = "OpenAIAudioSTS"

    # chat completion models
    name: str = "gpt-3.5-turbo"
    allowed_models: List[str] = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo",
        "gpt-4o-mini",
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-3.5-turbo-0125",
        # "chatgpt-4o-latest",
        # "gpt-3.5-turbo-instruct", # gpt-3.5-turbo-instruct does not support v1/chat/completions endpoint. only supports (/v1/completions)
        # "o1-preview",   # Does not support max_tokens and temperature
        # "o1-mini",      # Does not support max_tokens and temperature
        # "o1-preview-2024-09-12", # Does not support max_tokens and temperature
        # "o1-mini-2024-09-12",   # Does not support max_tokens and temperature
        # "gpt-4-0314",  #  it's deprecated
    ]

    # speech to text models
    sst_model_name: str = "whisper-1"
    allowed_stt_models: List[str] = ["whisper-1"]

    # text to speech models and voices
    tts_model_name: str = "tts-1"
    tts_voice: str = "alloy"
    allowed_tts_models: List[str] = ["tts-1", "tts-1-hd"]
    allowed_tts_voices: List[str] = [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
    ]

    def predict(
        self,
        audio_input_path: str,
        audio_output_path: str,
        system_prompt: Optional[str] = None,
    ) -> bytes:
        """
        Process speech input through the pipeline: speech-to-text, chat completion, and text-to-speech.

        Parameters:
            audio_input_path (str): Path to the input audio file.
            audio_output_path (str): Path to the output audio file.
            system_prompt (Optional[str]): Optional system prompt for the chat model.

        Returns:
            bytes: The generated speech audio as bytes.
        """

        try:
            # Step 1: Speech to Text
            stt_model = OpenAIAudio(api_key=self.api_key)
            stt_model.name = self.sst_model_name
            transcript = stt_model.predict(
                audio_path=audio_input_path, task="transcription"
            )

            # Step 2: Chat Completion
            chat_model = OpenAIModel(api_key=self.api_key)
            chat_model.name = self.name

            conversation = Conversation()

            if system_prompt:
                system_message = SystemMessage(content=system_prompt)
                conversation.add_message(system_message)

            human_message = HumanMessage(content=transcript)
            conversation.add_message(human_message)

            chat_model.predict(conversation=conversation)
            response_text = conversation.get_last().content

            # Step 3: Text to Speech
            tts_model = OpenAIAudioTTS(
                api_key=self.api_key, audio_path=audio_output_path
            )
            tts_model.name = self.tts_model_name
            audio_bytes = tts_model.predict(text=response_text)

            return audio_bytes

        except Exception as e:
            raise RuntimeError(f"Speech-to-Speech processing failed: {e}")
