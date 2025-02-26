import warnings

from typing import Literal, Optional, Any
from pydantic import Field
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(MessageBase, "ZeroMeasurement")
class FunctionMessage(MessageBase):
    content: str
    role: str = Field(default="tool")
    tool_call_id: str
    name: str
    type: Literal["FunctionMessage"] = "FunctionMessage"
    usage: Optional[Any] = (
        None  # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens, completion time, etc)
    )
