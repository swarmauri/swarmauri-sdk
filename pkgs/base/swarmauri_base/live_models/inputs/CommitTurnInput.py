from typing import Literal

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class CommitTurnInput(LiveInputBase):
    kind: Literal["commit_turn"] = "commit_turn"
    payload: None = None
    type: Literal["CommitTurnInput"] = "CommitTurnInput"
