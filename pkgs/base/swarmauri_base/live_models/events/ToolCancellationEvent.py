from typing import Literal, Optional

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class ToolCancellationEvent(LiveEventBase):
    kind: Literal["tool_cancellation"] = "tool_cancellation"
    call_id: str
    reason: Optional[str] = None
    type: Literal["ToolCancellationEvent"] = "ToolCancellationEvent"
