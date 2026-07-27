from typing import Awaitable, Callable, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ApprovalCallback = Callable[[str, dict], bool | Awaitable[bool]]


class ToolExecutionPolicy(BaseModel):
    require_approval: bool = False
    timeout: Optional[float] = Field(default=None, gt=0)
    approval_callback: Optional[ApprovalCallback] = None
    type: Literal["ToolExecutionPolicy"] = "ToolExecutionPolicy"
    model_config = ConfigDict(arbitrary_types_allowed=True)
