from typing import Any, Literal, Optional

from pydantic import BaseModel

ToolExecutionStatus = Literal[
    "completed",
    "denied",
    "failed",
    "timed_out",
    "cancelled",
]


class ToolExecutionResult(BaseModel):
    call_id: Optional[str] = None
    tool_name: Optional[str] = None
    status: ToolExecutionStatus = "completed"
    value: Any = None
    error: Optional[str] = None
    cancelled: bool = False
    type: Literal["ToolExecutionResult"] = "ToolExecutionResult"
