from typing import List, Literal, Union

from pydantic import ConfigDict, Field

from swarmauri_core.conversations.IConversation import IConversation
from swarmauri_base.ComponentBase import (
    ComponentBase,
    ResourceTypes,
    SubclassUnion,
)
from swarmauri_base.messages.MessageBase import MessageBase


@ComponentBase.register_model()
class ConversationBase(IConversation, ComponentBase):
    """
    Concrete implementation of IConversation, managing conversation history and
    operations.
    """

    messages: List[SubclassUnion[MessageBase]] = Field(
        default_factory=list,
        description="Messages retained by the conversation.",
    )
    resource: ResourceTypes = Field(default=ResourceTypes.CONVERSATION)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ConversationBase"] = "ConversationBase"

    @property
    def history(self) -> List[SubclassUnion[MessageBase]]:
        """
        Provides read-only access to the conversation history.
        """
        return self.messages

    @property
    def _history(self) -> List[SubclassUnion[MessageBase]]:
        """Return the stored messages for legacy conversation subclasses."""
        return self.messages

    @_history.setter
    def _history(self, messages: List[SubclassUnion[MessageBase]]) -> None:
        """Replace stored messages for legacy conversation subclasses."""
        self.messages = messages

    def add_message(self, message: SubclassUnion[MessageBase]):
        self.messages.append(message)

    def remove_message(self, message: SubclassUnion[MessageBase]):
        """
        Remove a message from the history

        @param message: Message to remove from the history
        @return None
        """
        if self.messages and message in self.messages:
            self.messages.remove(message)
        return None

    def add_messages(self, messages: List[SubclassUnion[MessageBase]]):
        for message in messages:
            self.messages.append(message)

    def get_last(self) -> Union[SubclassUnion[MessageBase], None]:
        if self.messages:
            return self.messages[-1]
        return None

    def clear_history(self):
        self.messages.clear()
