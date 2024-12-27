from pydantic import ConfigDict
from typing import Any, Optional, Union, Dict, Literal
import json
import logging
from swarmauri_core.messages import IMessage

from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.agents.AgentToolMixin import AgentToolMixin
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_core.typing import SubclassUnion
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.conversations.ConversationBase import ConversationBase

class ToolAgent(AgentToolMixin, AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    toolkit: SubclassUnion[ToolkitBase]
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolAgent'] = 'ToolAgent'
    
    def exec(self, 
        input_data: Optional[Union[str, IMessage]] = "",  
        llm_kwargs: Optional[Dict] = {}) -> Any:

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(content=input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        self.conversation.add_message(human_message)

        #predict a response        
        self.conversation = self.llm.predict(
            conversation=self.conversation, 
            toolkit=self.toolkit, 
            **llm_kwargs)

        logging.info(self.conversation.get_last().content)

        return self.conversation.get_last().content