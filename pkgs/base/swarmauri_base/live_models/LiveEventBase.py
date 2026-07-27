"""Base live-session event."""

from typing import Any, Dict, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.live_models.ILiveEvent import ILiveEvent


class LiveEventBase(ILiveEvent, ComponentBase):
    kind: str = "event"
    payload: Any = None
    correlation: Dict[str, Optional[str]] = Field(default_factory=dict)
    type: Literal["LiveEventBase"] = "LiveEventBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
