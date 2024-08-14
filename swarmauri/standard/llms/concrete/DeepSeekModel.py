import json
from typing import List, Dict, Literal
import openai 
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class DeepSeekModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['deepseek-chat', 
                                 'deepseek-coder', 
                                ]
    name: str = "deepseek-chat"
    type: Literal['DeepSeekModel'] = 'DeepSeekModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
       # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [message.model_dump(include=message_properties) for message in messages if message.role != 'system']
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == 'system':
                system_context = message.content
        return system_context

    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256, 
        frequency_penalty=0, 
        presence_penalty=0, 
        stop='\n', 
        stream=False, 
        top_p=1.0, 
        tools=list(), 
        tool_choice=None): 
        ''' 
        Args: 
            top_p (0.01 to 1.0)  Limit the pool of next tokens in each step to the top {top_p*100} percentile of possible tokens
            stop: stop the message when model generates one of these strings. 
            n: how many chat responses to generate
            stream: whether or not to stream the result, for long answers. if set to true n must be 1. 
        '''

        # Create client
        client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        
        # Get system_context from last message with system context in it
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        if system_context:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                system=system_context,
                temperature=temperature,
                max_tokens=max_tokens, 
                frequency_penalty=frequency_penalty,  
                presence_penalty=presence_penalty, 
                stop=stop, 
                stream=stream, 
                top_p=top_p, 
                tools=tools, 
                tool_choice=tool_choice
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens, 
                frequency_penalty=frequency_penalty,  
                presence_penalty=presence_penalty, 
                stop=stop, 
                stream=stream, 
                top_p=top_p, 
                tools=tools, 
                tool_choice=tool_choice
            )
        
        message_content = response.content[0].text
        conversation.add_message(AgentMessage(content=message_content))
        
        return conversation
