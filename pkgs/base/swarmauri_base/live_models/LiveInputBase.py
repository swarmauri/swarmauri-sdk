"""Base live-session input."""

from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.live_models.ILiveInput import ILiveInput

from swarmauri_base.ComponentBase import ComponentBase


class LiveInputBase(ILiveInput, ComponentBase):
    kind: str = "input"
    payload: Any = None
    mime_type: str | None = None
    correlation_id: str | None = Field(default=None)
    timestamp: float | None = None
    type: Literal["LiveInputBase"] = "LiveInputBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
