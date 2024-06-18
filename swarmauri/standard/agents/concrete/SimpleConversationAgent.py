from typing import Any, Optional, Dict

from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class SimpleConversationAgent(AgentConversationMixin, AgentBase):

    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        conversation = self.conversation
        llm = self.llm

        # Construct a new human message (for example purposes)
        if input_str:
            human_message = HumanMessage(content=input_str)
            conversation.add_message(human_message)
        
        messages = conversation.as_messages()
        prediction = llm.predict(messages=messages, **llm_kwargs)
        conversation.add_message(AgentMessage(content=prediction))
        return prediction