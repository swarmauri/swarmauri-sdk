from typing import Any, Optional
from abc import ABC

from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase

class ConversationAgentBase(AgentBase, IAgentConversation, ABC):
    def __init__(self, model: IModel, conversation: IConversation):
        AgentBase.__init__(self, model)
        self._conversation = conversation

    
    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
      

    @property
    def conversation(self) -> IConversation:
        return self._conversation

    @conversation.setter
    def conversation(self, value) -> None:
        self._conversation = value

