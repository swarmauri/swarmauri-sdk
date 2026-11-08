from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolExecutorBase import ToolExecutorBase


@ComponentBase.register_type(ToolExecutorBase, "ToolExecutor")
class ToolExecutor(ToolExecutorBase):
    """Execute tools with the standard SDK policy and lifecycle."""

    type: Literal["ToolExecutor"] = "ToolExecutor"
