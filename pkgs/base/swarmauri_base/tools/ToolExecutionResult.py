from typing import Any, Literal, Optional

from pydantic import BaseModel


class ToolExecutionResult(BaseModel):
    call_id: Optional[str] = None
    value: Any = None
    error: Optional[str] = None
    cancelled: bool = False
    type: Literal["ToolExecutionResult"] = "ToolExecutionResult"
