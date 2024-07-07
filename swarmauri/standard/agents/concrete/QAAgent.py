from typing import Any, Optional, Dict, Literal

from swarmauri.standard.conversations.concrete.MaxSizeConversation import MaxSizeConversation
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.agents.base.AgentBase import AgentBase

class QAAgent(AgentBase):
    conversation: MaxSizeConversation = MaxSizeConversation(max_size=2)
    type: Literal['QAAgent'] = 'QAAgent'
    
    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        
        self.conversation.add_message(HumanMessage(content=input_str))
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        
        return self.conversation.get_last().content