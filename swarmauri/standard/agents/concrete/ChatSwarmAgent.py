from typing import Any, Optional, Union, Dict
from swarmauri.core.models.IModel import IModel
from swarmauri.core.messages import IMessage
from swarmauri.core.conversations import IConversation
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage

class ChatSwarmAgent(ConversationAgentBase):
    def __init__(self, model: IModel, conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_data: Union[str, IMessage], model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        return prediction