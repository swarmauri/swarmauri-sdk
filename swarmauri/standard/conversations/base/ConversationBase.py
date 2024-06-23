from typing import List, Union
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
    
    @property
    def history(self) -> List[IMessage]:
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

    def as_messages(self) -> List[dict]:
        message_include=['role', 'content', 'tool_call_id', 'tool_calls', 'name']
        return [message.dict(include=message_include) for message in self.history]
