from typing import Any, Dict, Literal, Mapping, Optional

from pydantic import BaseModel, Field


class ToolExecutionRequest(BaseModel):
    call_id: Optional[str] = None
    tool_name: str
    arguments: Mapping[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    provider_name: Optional[str] = None
    correlation: Dict[str, Optional[str]] = Field(default_factory=dict)
    type: Literal["ToolExecutionRequest"] = "ToolExecutionRequest"
