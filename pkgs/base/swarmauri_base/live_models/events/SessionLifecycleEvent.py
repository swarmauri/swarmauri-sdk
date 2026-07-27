from typing import Literal

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class SessionLifecycleEvent(LiveEventBase):
    kind: Literal["session_lifecycle"] = "session_lifecycle"
    state: str
    type: Literal["SessionLifecycleEvent"] = "SessionLifecycleEvent"
