from typing import Literal

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class TextDeltaEvent(LiveEventBase):
    kind: Literal["text_delta"] = "text_delta"
    payload: str
    type: Literal["TextDeltaEvent"] = "TextDeltaEvent"
