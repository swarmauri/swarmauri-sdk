from typing import Literal, Optional

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class SessionResumptionEvent(LiveEventBase):
    kind: Literal["session_resumption"] = "session_resumption"
    token: Optional[str] = None
    resumable: bool = False
    type: Literal["SessionResumptionEvent"] = "SessionResumptionEvent"
