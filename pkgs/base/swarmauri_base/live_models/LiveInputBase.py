"""Base live-session input."""

from typing import Any, Literal, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.live_models.ILiveInput import ILiveInput


class LiveInputBase(ILiveInput, ComponentBase):
    kind: str = "input"
    payload: Any = None
    mime_type: Optional[str] = None
    correlation_id: Optional[str] = Field(default=None)
    timestamp: Optional[float] = None
    type: Literal["LiveInputBase"] = "LiveInputBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
