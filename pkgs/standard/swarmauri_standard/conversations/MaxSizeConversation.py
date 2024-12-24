from typing import Literal
from pydantic import Field
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.conversations.IMaxSize import IMaxSize

class MaxSizeConversation(IMaxSize, ConversationBase):
    max_size: int = Field(default=2, gt=1)
    type: Literal['MaxSizeConversation'] = 'MaxSizeConversation'

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