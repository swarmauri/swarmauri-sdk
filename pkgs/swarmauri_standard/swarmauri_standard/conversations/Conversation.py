from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase


@ComponentBase.register_type(ConversationBase, "Conversation")
class Conversation(ConversationBase):
    """
    Concrete implementation of ConversationBase, managing conversation history
    and operations.
    """

    type: Literal["Conversation"] = "Conversation"
