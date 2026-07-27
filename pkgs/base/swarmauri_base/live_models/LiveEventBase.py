"""Base live-session event."""

from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.live_models.ILiveEvent import ILiveEvent

from swarmauri_base.ComponentBase import ComponentBase


class LiveEventBase(ILiveEvent, ComponentBase):
    kind: str = "event"
    payload: Any = None
    correlation: dict[str, str | None] = Field(default_factory=dict)
    type: Literal["LiveEventBase"] = "LiveEventBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
