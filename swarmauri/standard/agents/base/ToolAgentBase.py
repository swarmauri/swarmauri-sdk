from abc import ABC
from typing import Any, Optional
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase


class ToolAgentBase(ConversationAgentBase, IAgentConversation, ABC):
    
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation,
                 toolkit: IToolkit):
        ConversationAgentBase.__init__(self, model, conversation)
        self._toolkit = toolkit

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def toolkit(self) -> IToolkit:
        return self._toolkit
    
    @toolkit.setter
    def toolkit(self, value) -> None:
        self._toolkit = value        
