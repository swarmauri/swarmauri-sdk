from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolExecutionRequest(BaseModel):
    call_id: str | None = None
    tool_name: str
    arguments: Mapping[str, Any] = Field(default_factory=dict)
    session_id: str | None = None
    conversation_id: str | None = None
    provider_name: str | None = None
    correlation: dict[str, str | None] = Field(default_factory=dict)
    type: Literal["ToolExecutionRequest"] = "ToolExecutionRequest"
