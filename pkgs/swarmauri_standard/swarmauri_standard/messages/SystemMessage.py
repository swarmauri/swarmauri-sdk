import warnings

from typing import Literal
from pydantic import Field
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(MessageBase, "SystemMessage")
class SystemMessage(MessageBase):
    content: str
    role: str = Field(default="system")
    type: Literal["SystemMessage"] = "SystemMessage"
