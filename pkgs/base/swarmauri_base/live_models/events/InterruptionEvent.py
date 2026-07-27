from typing import Literal, Optional

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class InterruptionEvent(LiveEventBase):
    kind: Literal["interruption"] = "interruption"
    reason: Optional[str] = None
    type: Literal["InterruptionEvent"] = "InterruptionEvent"
