import warnings

from typing import Literal
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(ConversationBase, "Conversation")
class Conversation(ConversationBase):
    """
    Concrete implementation of ConversationBase, managing conversation history and operations.
    """

    type: Literal["Conversation"] = "Conversation"
