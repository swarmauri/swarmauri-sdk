from typing import Any, Dict, Literal

from pydantic import Field

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class ToolCallEvent(LiveEventBase):
    kind: Literal["tool_call"] = "tool_call"
    call_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    type: Literal["ToolCallEvent"] = "ToolCallEvent"
