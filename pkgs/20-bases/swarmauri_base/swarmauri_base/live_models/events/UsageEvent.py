from typing import Literal

from pydantic import Field

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class UsageEvent(LiveEventBase):
    kind: Literal["usage"] = "usage"
    payload: dict[str, int] = Field(default_factory=dict)
    type: Literal["UsageEvent"] = "UsageEvent"
