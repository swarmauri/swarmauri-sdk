from typing import Literal

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class InterruptionEvent(LiveEventBase):
    kind: Literal["interruption"] = "interruption"
    reason: str | None = None
    type: Literal["InterruptionEvent"] = "InterruptionEvent"
