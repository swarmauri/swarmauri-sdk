from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri_base.messages.MessageBase import MessageBase

class SystemMessage(MessageBase):
    content: str
    role: str = Field(default='system')
    type: Literal['SystemMessage'] = 'SystemMessage'