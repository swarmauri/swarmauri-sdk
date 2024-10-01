from typing import Any, Optional, Dict, Literal
from swarmauri.agents.base.AgentBase import AgentBase
from swarmauri.conversations.concrete.MaxSystemContextConversation import MaxSystemContextConversation
from swarmauri.messages.concrete.HumanMessage import HumanMessage


class QAAgent(AgentBase):
    conversation: MaxSystemContextConversation = MaxSystemContextConversation(max_size=2)
    type: Literal['QAAgent'] = 'QAAgent'

    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        self.conversation.add_message(HumanMessage(content=input_str))
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        
        return self.conversation.get_last().content
