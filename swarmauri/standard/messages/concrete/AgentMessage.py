from typing import Optional, Any
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class AgentMessage(MessageBase):
    content: str
    role: str = Field(default='assistant')
    tool_calls: Optional[Any] = None