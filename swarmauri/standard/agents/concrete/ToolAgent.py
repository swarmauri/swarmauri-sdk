from typing import Any, Optional, Union, Dict
import json

from swarmauri.core.models.IModel import IModel
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.ToolAgentBase import ToolAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class ToolAgent(AgentBase, ConversationAgentBase, ToolAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation, 
                 toolkit: IToolkit):
        AgentBase.__init__(self, model=model)
        ConversationAgentBase.__init__(self, conversation=conversation)
        ToolAgentBase.__init__(self, toolkit=toolkit)

    def exec(self, input_data: Union[str, IMessage],  model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model
        toolkit = self.toolkit
        

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
        messages = conversation.as_messages()
        
        prediction = model.predict(messages=messages, 
                                   tools=toolkit.tools, 
                                   tool_choice="auto", 
                                   **model_kwargs)
        
        prediction_message = prediction.choices[0].message
        
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message.content, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
            
            messages = conversation.as_messages()
            rag_prediction = model.predict(messages=messages, 
                                           tools=toolkit.tools, 
                                           tool_choice="none",
                                           **model_kwargs)
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            agent_message = AgentMessage(agent_response)
            conversation.add_message(agent_message)
            prediction = rag_prediction
            
        return agent_response 
    