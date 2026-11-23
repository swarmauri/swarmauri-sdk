from typing import Any, Literal

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class ToolResultInput(LiveInputBase):
    kind: Literal["tool_result"] = "tool_result"
    call_id: str
    payload: Any
    is_error: bool = False
    type: Literal["ToolResultInput"] = "ToolResultInput"
