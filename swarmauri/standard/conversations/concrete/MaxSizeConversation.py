from swarmauri.converastions.base.ConversationBase import ConversationBase
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize

class MaxSizeConversation(ConversationBase, IMaxSize):
    def __init__(self, max_size: int):
        super().__init__()

        self._max_size = max_size
        
    @property
    def max_size(self) -> int:
        """
        Provides read-only access to the conversation history.
        """
        return self._max_size
    
    @max_size.setter
    def max_size(self, new_max_size: int) -> int:
        """
        Provides read-only access to the conversation history.
        """
        if new_max_size > 0:
            self._max_size = int
        else:
            raise ValueError('Cannot set conversation size to 0.')


    def add_message(self, message: IMessage):
        """Adds a message and ensures the conversation does not exceed the max size."""
        super().add_message(message)
        self._enforce_max_size_limit()

    def _enforce_max_size_limit(self):
        """
        Enforces the maximum size limit of the conversation history.
        If the current history size exceeds the maximum size, the oldest messages are removed.
        We pop two messages (one for the user's prompt, one for the assistant's response)
        """
        while len(self._history) > self.max_size:
            
            self._history.pop(0)
            self._history.pop(0)