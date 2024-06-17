from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class SystemMessage(MessageBase):
    content: str
    role: str = Field(default='system')