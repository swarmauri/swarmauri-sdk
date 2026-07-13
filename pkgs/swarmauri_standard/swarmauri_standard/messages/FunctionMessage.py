from typing import Any, Literal, Optional

from pydantic import Field

from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(MessageBase, "FunctionMessage")
class FunctionMessage(MessageBase):
    content: str
    role: Literal["tool"] = Field(default="tool")
    tool_call_id: str
    name: str
    type: Literal["FunctionMessage"] = "FunctionMessage"
    usage: Optional[Any] = (
        # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens,
        # completion time, etc)
        None
    )
