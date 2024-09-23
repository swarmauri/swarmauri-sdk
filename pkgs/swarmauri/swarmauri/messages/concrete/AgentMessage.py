from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.messages.base.MessageBase import MessageBase

class AgentMessage(MessageBase):
    content: Optional[str] = None
    role: str = Field(default='assistant')
    #tool_calls: Optional[Any] = None
    name: Optional[str] = None
    type: Literal['AgentMessage'] = 'AgentMessage'
    usage: Optional[Any] = None # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens, completion time, etc)