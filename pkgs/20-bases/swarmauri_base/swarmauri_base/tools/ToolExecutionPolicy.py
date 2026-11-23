from collections.abc import Awaitable, Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .ToolExecutionRequest import ToolExecutionRequest

ApprovalCallback = Callable[[ToolExecutionRequest], bool | Awaitable[bool]]


class ToolExecutionPolicy(BaseModel):
    require_approval: bool = False
    deny_without_callback: bool = True
    timeout: float | None = Field(default=None, gt=0)
    approval_callback: ApprovalCallback | None = None
    type: Literal["ToolExecutionPolicy"] = "ToolExecutionPolicy"
    model_config = ConfigDict(arbitrary_types_allowed=True)
