from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase


class FunctionMessage(MessageBase):
    content: str
    name: str
    tool_call_id: str
    role: str = Field(default='tool')
