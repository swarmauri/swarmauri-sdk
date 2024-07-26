from typing import Any, Optional, Dict, Literal

from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion # 🚧  Placeholder
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase # 🚧  Placeholder

class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
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