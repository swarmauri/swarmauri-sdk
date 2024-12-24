from typing import List, Union, Literal
from pydantic import Field, PrivateAttr, ConfigDict
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.conversations.IConversation import IConversation


class ConversationBase(IConversation, ComponentBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """

    _history: List[SubclassUnion[MessageBase]] = PrivateAttr(default_factory=list)
    resource: ResourceTypes = Field(default=ResourceTypes.CONVERSATION.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ConversationBase"] = "ConversationBase"

    @property
    def history(self) -> List[SubclassUnion[MessageBase]]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history

    def add_message(self, message: SubclassUnion[MessageBase]):
        self._history.append(message)
        
    def remove_message(self, message: SubclassUnion[MessageBase]):
        """ 
        Remove a message from the history
        
        @param message: Message to remove from the history
        @return None
        """
        if self._history and message in self._history:
            self._history.remove(message)
        return None

    def add_messages(self, messages: List[SubclassUnion[MessageBase]]):
        for message in messages:
            self._history.append(message)

    def get_last(self) -> Union[SubclassUnion[MessageBase], None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()
