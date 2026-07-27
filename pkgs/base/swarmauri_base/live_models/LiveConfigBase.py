"""Provider-neutral live-session configuration."""

from typing import Any, Dict, List, Literal

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.live_models.ILiveConfig import ILiveConfig


class LiveConfigBase(ILiveConfig, ComponentBase):
    requested_modalities: List[str] = Field(default_factory=lambda: ["text"])
    tools: List[Any] = Field(default_factory=list)
    initial_history: List[Any] = Field(default_factory=list)
    provider_options: Dict[str, Any] = Field(default_factory=dict)
    vad: Dict[str, Any] = Field(default_factory=dict)
    transcription: Dict[str, Any] = Field(default_factory=dict)
    tool_policy: Dict[str, Any] = Field(default_factory=dict)
    type: Literal["LiveConfigBase"] = "LiveConfigBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
