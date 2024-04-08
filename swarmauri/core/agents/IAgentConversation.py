from abc import ABC, abstractmethod
from swarmauri.core.conversations.IConversation import IConversation

class IAgentConversation(ABC):
    
    @property
    @abstractmethod
    def conversation(self) -> IConversation:
        """
        The conversation property encapsulates the agent's ongoing dialogue or interaction context.
        """
        pass

    @conversation.setter
    @abstractmethod
    def conversation(self) -> IConversation:
        pass