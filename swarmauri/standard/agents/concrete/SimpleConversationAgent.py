from typing import Any, Optional, Dict

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase
from swarmauri.standard.messages.concrete import HumanMessage

class SimpleConversationAgent(AgentBase, ConversationAgentBase, NamedAgentBase):
    def __init__(self, model: IModel, conversation: IConversation, name: str):
        AgentBase.__init__(self, model=model)
        ConversationAgentBase.__init__(self, conversation=conversation)
        NamedAgentBase.__init__(self, name=name)

    def exec(self, 
        input_str: Optional[str] = None,
        model_kwargs: Optional[Dict] = {}
        ) -> Any:
        conversation = self.conversation
        model = self.model

        # Construct a new human message (for example purposes)
        if input_str:
            human_message = HumanMessage(input_str)
            conversation.add_message(human_message)
        
        messages = conversation.as_messages()
        prediction = model.predict(messages=messages, **model_kwargs)
        return prediction