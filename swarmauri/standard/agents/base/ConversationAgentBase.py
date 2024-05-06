from abc import ABC

from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.conversations.IConversation import IConversation

class ConversationAgentBase(IAgentConversation, ABC):
    def __init__(self, conversation: IConversation):
        self._conversation = conversation

    @property
    def conversation(self) -> IConversation:
        return self._conversation

    @conversation.setter
    def conversation(self, value) -> None:
        self._conversation = value

