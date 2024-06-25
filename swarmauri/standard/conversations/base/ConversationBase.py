from typing import List, Union, Literal
from pydantic import Field, PrivateAttr
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ComponentBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    _history: List[SubclassUnion[MessageBase]] = PrivateAttr(default_factory=list)
    resource: ResourceTypes =  Field(default=ResourceTypes.CONVERSATION.value)
    type: Literal['ConversationBase'] = 'ConversationBase'

    @property
    def history(self) -> List[SubclassUnion[MessageBase]]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history
    
    def add_message(self, message: SubclassUnion[MessageBase]):
        self._history.append(message)

    def get_last(self) -> Union[SubclassUnion[MessageBase], None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()
