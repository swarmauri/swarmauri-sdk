from typing import Optional, Any
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase


class AgentMessage(MessageBase):
    content: str
    tool_calls: Optional[Any] = None
    role: str = Field(default='assistant')

    @property
    def role(self) -> str:
        return self._role