"""Use ordered voice/text turns on ElevenLabs' dialogue endpoints."""

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.HttpTTSMixin import HttpTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


class DialogueTurn(BaseModel):
    """An immutable turn; tuples of turns can be used as batch keys."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    text: str = Field(min_length=1)
    voice_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")

    @field_validator("text")
    @classmethod
    def _nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Dialogue text must not be blank.")
        return value


DialogueInput = str | tuple[DialogueTurn, ...]


@ComponentBase.register_type(TTSBase, "ElevenLabsDialogueTTS")
class ElevenLabsDialogueTTS(HttpTTSMixin, TTSBase):
    """Accept typed turn tuples, or a string using default_voice_id."""

    api_key: SecretStr = Field(repr=False, min_length=1)
    timeout: float = Field(default=120, gt=0)
    allowed_models: list[str] = ["eleven_v4", "eleven_v3"]
    name: str = Field(default="eleven_v4", min_length=1)
    default_voice_id: str | None = Field(
        default=None, pattern=r"^[A-Za-z0-9_-]+$"
    )
    output_format: Literal["mp3_44100_128", "pcm_24000", "ulaw_8000"] = (
        "mp3_44100_128"
    )
    type: Literal["ElevenLabsDialogueTTS"] = "ElevenLabsDialogueTTS"

    def _speech_endpoint(self, streaming: bool) -> str:
        suffix = "/stream" if streaming else ""
        return str(
            httpx.URL(
                f"https://api.elevenlabs.io/v1/text-to-dialogue{suffix}",
                params={"output_format": self.output_format},
            )
        )

    def _speech_headers(self) -> dict[str, str]:
        return {
            "xi-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    def _payload(self, text: DialogueInput, streaming: bool) -> dict[str, Any]:
        if isinstance(text, str):
            if self.default_voice_id is None:
                raise ValueError(
                    "String input requires default_voice_id; "
                    "use a tuple of DialogueTurn for dialogue."
                )
            turns = (DialogueTurn(text=text, voice_id=self.default_voice_id),)
        elif (
            isinstance(text, tuple)
            and text
            and all(isinstance(turn, DialogueTurn) for turn in text)
        ):
            turns = text
        else:
            raise ValueError(
                "Expected text or a nonempty tuple of DialogueTurn."
            )
        if len({turn.voice_id for turn in turns}) > 10:
            raise ValueError("Dialogue accepts at most ten unique voices.")
        if sum(len(turn.text) for turn in turns) > 2000:
            raise ValueError(
                "Dialogue is limited to 2000 characters "
                "for reliable generation."
            )
        return {
            "inputs": [turn.model_dump() for turn in turns],
            "model_id": self.name,
        }

    def predict(
        self, text: DialogueInput, audio_path: str = "output.mp3"
    ) -> str:
        return super().predict(text, audio_path)

    async def apredict(
        self, text: DialogueInput, audio_path: str = "output.mp3"
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
