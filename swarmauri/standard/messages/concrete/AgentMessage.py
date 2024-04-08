from typing import Optional, Any
from swarmauri.standard.messages.base.MessageBase import MessageBase


class AgentMessage(MessageBase):
    def __init__(self, content, tool_calls: Optional[Any] = None):
        super().__init__(role='assistant', content=content)
        if tool_calls:
            self.tool_calls = tool_calls