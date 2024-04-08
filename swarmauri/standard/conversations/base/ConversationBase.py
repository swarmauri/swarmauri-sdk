from abc import ABC
from typing import List, Union
from ....core.messages.IMessage import IMessage
from ....core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ABC):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
        self._history: List[IMessage] = []

    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history
    
    def add_message(self, message: IMessage):
        self._history.append(message)

    def get_last(self) -> Union[IMessage, None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()

    def as_dict(self) -> List[dict]:
        return [message.as_dict() for message in self.history] # This must utilize the public self.history
    
    
    # def __repr__(self):
        # return repr([message.as_dict() for message in self._history])