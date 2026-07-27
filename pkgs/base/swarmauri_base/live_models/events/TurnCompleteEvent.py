from typing import Literal

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class TurnCompleteEvent(LiveEventBase):
    kind: Literal["turn_complete"] = "turn_complete"
    type: Literal["TurnCompleteEvent"] = "TurnCompleteEvent"
