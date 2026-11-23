"""Provider-neutral live-session configuration."""

from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.live_models.ILiveConfig import ILiveConfig

from swarmauri_base.ComponentBase import ComponentBase


class LiveConfigBase(ILiveConfig, ComponentBase):
    requested_modalities: list[str] = Field(default_factory=lambda: ["text"])
    tools: list[Any] = Field(default_factory=list)
    initial_history: list[Any] = Field(default_factory=list)
    provider_options: dict[str, Any] = Field(default_factory=dict)
    vad: dict[str, Any] = Field(default_factory=dict)
    transcription: dict[str, Any] = Field(default_factory=dict)
    tool_policy: dict[str, Any] = Field(default_factory=dict)
    type: Literal["LiveConfigBase"] = "LiveConfigBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
