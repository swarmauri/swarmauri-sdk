from typing import Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase


class FunctionMessage(MessageBase):
    content: str
    role: str = Field(default='tool')
    tool_call_id: str
    name: str
    type: Literal['FunctionMessage'] = 'FunctionMessage'    
