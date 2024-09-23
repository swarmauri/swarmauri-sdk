from typing import Any, Optional, Dict, Literal

from swarmauri_core.conversations.IConversation import IConversation
from swarmauri.agents.base.AgentBase import AgentBase
from swarmauri.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri_core.typing import SubclassUnion 
from swarmauri.conversations.base.ConversationBase import ConversationBase

class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    conversation: SubclassUnion[ConversationBase] #
    type: Literal['SimpleConversationAgent'] = 'SimpleConversationAgent'
    
    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        if input_str:
            human_message = HumanMessage(content=input_str)
            self.conversation.add_message(human_message)
        
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content