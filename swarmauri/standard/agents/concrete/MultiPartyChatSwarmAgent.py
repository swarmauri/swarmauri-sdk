from typing import Any, Optional, Union, Dict


from swarmauri.standard.conversations.concrete.SharedConversation import SharedConversation
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase

from swarmauri.core.models.IModel import IModel
from swarmauri.core.messages import IMessage


class MultiPartyChatSwarmAgent(AgentBase, ConversationAgentBase, NamedAgentBase):
    def __init__(self, name: str, model: IModel, conversation: SharedConversation):
        AgentBase.__init__(self, model=model)
        ConversationAgentBase.__init__(self, conversation=conversation)
        NamedAgentBase.__init__(self, name=name)

    def exec(self, input_data: Union[str, IMessage] = "", model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        if input_data != "":
            # we add the sender's name as the id so we can keep track of who said what in the conversation
            conversation.add_message(human_message, sender_id=self.name)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_messages()

        
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        if prediction != '':
            agent_message = AgentMessage(prediction)
            conversation.add_message(agent_message, sender_id=self.name)
        
        return prediction