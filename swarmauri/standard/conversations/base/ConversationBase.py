import warnings
import uuid
from abc import ABC
from typing import List, Union
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ABC):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
        self._history: List[IMessage] = []
        self._id = uuid.uuid4()  # Assign a unique UUID to each instance

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

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

    def as_messages(self) -> List[dict]:
        return [message.as_dict() for message in self.history]

    def as_dict(self) -> List[dict]:
        print('USE TO_DICT NOW')
        warnings.warn("""This function is deprecated and will be removed in a future version.
            USE .to_dict() now
            """,
                  DeprecationWarning, stacklevel=2)
        return [message.as_dict() for message in self.history]
    
    def to_dict(self) -> List[dict]:
        # We will need to update this to enable the ability to export and import functions
        # We need to use a new interface besides to_dict() that enables conversations
        return [message.as_dict() for message in self.history]

    @classmethod
    def from_dict(cls, data):
        #data.pop("type", None)
        #return cls(**data)
        raise NotImplementedError('from_dict load not implemented on this class yet')
