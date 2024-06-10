from dataclasses import dataclass
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.conversations.IConversation import IConversation

@dataclass
class ConversationAgentBase(IAgentConversation):
    conversation: IConversation

    def __post_init__(self):
        if type(self.conversation) == property:
            raise ValueError('Conversation is required.')

    @property
    def conversation(self) -> IConversation:
        return self._conversation

    @conversation.setter
    def conversation(self, value) -> None:
        self._conversation = value