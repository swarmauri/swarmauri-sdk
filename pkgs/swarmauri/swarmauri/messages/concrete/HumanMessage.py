from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    content: str
    role: str = Field(default='user')
    name: Optional[str] = None
    type: Literal['HumanMessage'] = 'HumanMessage'    