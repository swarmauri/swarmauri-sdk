from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RealtimeTurn(BaseModel):
    output_text: str = ""
    input_transcript: str = ""
    output_transcript: str = ""
    audio_chunks: list[bytes] = Field(default_factory=list)
    tool_calls: list[Any] = Field(default_factory=list)
    usage: dict[str, int] = Field(default_factory=dict)
    interrupted: bool = False
    completed: bool = False
    model_config = ConfigDict(arbitrary_types_allowed=True)
