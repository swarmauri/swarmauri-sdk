from typing import Awaitable, Callable, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .ToolExecutionRequest import ToolExecutionRequest

ApprovalCallback = Callable[[ToolExecutionRequest], bool | Awaitable[bool]]


class ToolExecutionPolicy(BaseModel):
    require_approval: bool = False
    deny_without_callback: bool = True
    timeout: Optional[float] = Field(default=None, gt=0)
    approval_callback: Optional[ApprovalCallback] = None
    type: Literal["ToolExecutionPolicy"] = "ToolExecutionPolicy"
    model_config = ConfigDict(arbitrary_types_allowed=True)
