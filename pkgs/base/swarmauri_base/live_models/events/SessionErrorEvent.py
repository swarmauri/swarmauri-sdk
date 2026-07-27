from typing import Literal, Optional

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class SessionErrorEvent(LiveEventBase):
    kind: Literal["session_error"] = "session_error"
    message: str
    code: Optional[str] = None
    recoverable: bool = False
    type: Literal["SessionErrorEvent"] = "SessionErrorEvent"
