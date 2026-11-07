from typing import Literal

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class InterruptInput(LiveInputBase):
    kind: Literal["interrupt"] = "interrupt"
    payload: None = None
    type: Literal["InterruptInput"] = "InterruptInput"
