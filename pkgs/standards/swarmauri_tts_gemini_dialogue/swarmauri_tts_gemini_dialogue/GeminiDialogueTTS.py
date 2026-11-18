"""Gemini Interactions dialogue with labelled turns and speaker bindings."""

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any, ClassVar, Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_tts_gemini import GeminiTTS


class GeminiDialogueTurn(BaseModel):
    """An immutable labelled transcript turn, optionally with its own style."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    text: str = Field(min_length=1)
    speaker: str = Field(min_length=1)
    style: str | None = Field(default=None, min_length=1)

    @field_validator("text", "speaker", "style")
    @classmethod
    def _nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError(
                "Dialogue text, speaker and style must not be blank."
            )
        return value


DialogueInput = str | tuple[GeminiDialogueTurn, ...]


@ComponentBase.register_type(TTSBase, "GeminiDialogueTTS")
class GeminiDialogueTTS(GeminiTTS):
    """Share Gemini's decoder while owning the structured speaker contract."""

    type: Literal["GeminiDialogueTTS"] = "GeminiDialogueTTS"
    # Replace the inherited single-speaker setting with explicit bindings.
    voice: ClassVar[str] = ""
    speaker_voices: dict[str, str] = Field(min_length=2, max_length=2)
    default_speaker: str | None = None

    @model_validator(mode="after")
    def _validate_speakers(self):
        if any(
            not key.strip() or not value.strip()
            for key, value in self.speaker_voices.items()
        ):
            raise ValueError(
                "Speaker labels and voice bindings must not be blank."
            )
        if (
            self.default_speaker is not None
            and self.default_speaker not in self.speaker_voices
        ):
            raise ValueError("default_speaker must have a voice binding.")
        return self

    def _payload(self, text: DialogueInput, streaming: bool) -> dict[str, Any]:
        if isinstance(text, str):
            if self.default_speaker is None:
                raise ValueError("String input requires default_speaker.")
            turns = (
                GeminiDialogueTurn(text=text, speaker=self.default_speaker),
            )
        elif (
            isinstance(text, tuple)
            and text
            and all(isinstance(turn, GeminiDialogueTurn) for turn in text)
        ):
            turns = text
        else:
            raise ValueError(
                "Expected text or a nonempty tuple of GeminiDialogueTurn."
            )
        content = []
        for turn in turns:
            if turn.speaker not in self.speaker_voices:
                raise ValueError(
                    "Every dialogue speaker needs a voice binding."
                )
            annotation = {"type": "speech_metadata", "speaker": turn.speaker}
            style = turn.style if turn.style is not None else self.style
            if style is not None:
                annotation["style"] = style
            content.append(
                {
                    "type": "text",
                    "text": turn.text,
                    "annotations": [annotation],
                }
            )
        return {
            "model": self.name,
            "input": [{"type": "user_input", "content": content}],
            "response_format": {
                "type": "audio",
                "mime_type": "audio/l16" if streaming else "audio/wav",
                "sample_rate": 24000,
            },
            "generation_config": {
                "speech_config": {
                    "speakers": [
                        {"speaker": speaker, "voice": voice}
                        for speaker, voice in self.speaker_voices.items()
                    ]
                }
            },
            "stream": streaming,
            "store": False,
        }

    def predict(
        self, text: DialogueInput, audio_path: str = "output.wav"
    ) -> str:
        return super().predict(text, audio_path)

    async def apredict(
        self, text: DialogueInput, audio_path: str = "output.wav"
    ) -> str:
        return await super().apredict(text, audio_path)

    def stream(self, text: DialogueInput) -> Iterator[bytes]:
        return super().stream(text)

    async def astream(self, text: DialogueInput) -> AsyncIterator[bytes]:
        # Explicitly close the inner iterator when callers cancel this wrapper.
        iterator = super().astream(text)
        try:
            async for chunk in iterator:
                yield chunk
        finally:
            await iterator.aclose()

    def batch(self, text_path_dict: Mapping[DialogueInput, str]) -> list[str]:
        return super().batch(text_path_dict)

    async def abatch(
        self,
        text_path_dict: Mapping[DialogueInput, str],
        max_concurrent: int = 5,
    ) -> list[str]:
        return await super().abatch(text_path_dict, max_concurrent)
