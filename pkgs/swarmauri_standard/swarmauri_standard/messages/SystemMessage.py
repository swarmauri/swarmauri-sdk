from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase


@ComponentBase.register_type(MessageBase, "SystemMessage")
class SystemMessage(MessageBase):
    content: str
    role: str = Field(default="system")
    type: Literal["SystemMessage"] = "SystemMessage"
