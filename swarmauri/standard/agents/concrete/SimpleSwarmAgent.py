from typing import Any, Optional

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation


from swarmauri.standard.agents.base.SwarmAgentBase import AgentBase
from swarmauri.standard.messages.concrete import HumanMessage

class SimpleSwarmAgent(AgentBase):
    def __init__(self, model: IModel, 
                 conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_str: Optional[str] = None) -> Any:
        conversation = self.conversation
        model = self.model

        # Construct a new human message (for example purposes)
        if input_str:
            human_message = HumanMessage(input_str)
            conversation.add_message(human_message)
        
        messages = conversation.as_dict()
        prediction = model.predict(messages=messages)
        return prediction