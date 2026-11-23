from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ._internal.RealtimeTurn import RealtimeTurn


class RealtimeAgentRunResult(BaseModel):
    turn: RealtimeTurn
    events: list[Any] = Field(default_factory=list)
    type: Literal["RealtimeAgentRunResult"] = "RealtimeAgentRunResult"
    model_config = ConfigDict(arbitrary_types_allowed=True)
