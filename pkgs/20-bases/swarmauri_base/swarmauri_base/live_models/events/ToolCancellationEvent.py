from typing import Literal

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class ToolCancellationEvent(LiveEventBase):
    kind: Literal["tool_cancellation"] = "tool_cancellation"
    call_id: str
    reason: str | None = None
    type: Literal["ToolCancellationEvent"] = "ToolCancellationEvent"
