from typing import Optional, Any
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    content: str
    name: str = Field(default='user')
    role: str = Field(default='user')
    tool_calls: Optional[Any] = None
