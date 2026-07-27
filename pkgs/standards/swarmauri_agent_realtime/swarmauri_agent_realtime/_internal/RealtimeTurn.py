from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class RealtimeTurn(BaseModel):
    output_text: str = ""
    input_transcript: str = ""
    output_transcript: str = ""
    audio_chunks: List[bytes] = Field(default_factory=list)
    tool_calls: List[Any] = Field(default_factory=list)
    usage: Dict[str, int] = Field(default_factory=dict)
    interrupted: bool = False
    completed: bool = False
    model_config = ConfigDict(arbitrary_types_allowed=True)
