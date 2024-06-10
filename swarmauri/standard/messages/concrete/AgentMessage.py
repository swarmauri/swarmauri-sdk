from typing import Optional, Any
from swarmauri.standard.messages.base.MessageBase import MessageBase


class AgentMessage(MessageBase):
    content: str
    tool_calls: Optional[Any] = None
    _role: str ='assistant'

    @property
    def role(self) -> str:
        return self._role