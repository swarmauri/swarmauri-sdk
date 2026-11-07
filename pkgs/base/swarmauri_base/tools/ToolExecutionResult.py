from typing import Any, Literal

from pydantic import BaseModel

ToolExecutionStatus = Literal[
    "completed",
    "denied",
    "failed",
    "timed_out",
    "cancelled",
]


class ToolExecutionResult(BaseModel):
    call_id: str | None = None
    tool_name: str | None = None
    status: ToolExecutionStatus = "completed"
    value: Any = None
    error: str | None = None
    cancelled: bool = False
    type: Literal["ToolExecutionResult"] = "ToolExecutionResult"
