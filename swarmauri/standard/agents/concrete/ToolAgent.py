from typing import Any, Optional, Union, Dict, Literal
import json
from pydantic import ConfigDict
from swarmauri.core.messages import IMessage

from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentToolMixin import AgentToolMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class ToolAgent(AgentToolMixin, AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    toolkit: SubclassUnion[Toolkit]
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolAgent'] = 'ToolAgent'
    
    def exec(self, 
        input_data: Optional[Union[str, IMessage]] = "",  
        llm_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        llm = self.llm
        toolkit = self.toolkit

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(content=input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)

        #predict a response        
        agent_response = llm.predict(messages=conversation.history, 
                                   toolkit=toolkit, 
                                   **llm_kwargs)
        return agent_response