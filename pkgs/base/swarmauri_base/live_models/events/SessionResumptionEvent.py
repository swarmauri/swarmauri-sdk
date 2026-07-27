from typing import Literal

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class SessionResumptionEvent(LiveEventBase):
    kind: Literal["session_resumption"] = "session_resumption"
    token: str | None = None
    resumable: bool = False
    type: Literal["SessionResumptionEvent"] = "SessionResumptionEvent"
