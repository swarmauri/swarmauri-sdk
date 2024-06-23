import json
from typing import List, Dict
from openai import OpenAI
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class OpenAIModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-4-32k',
    'gpt-4-32k-0613',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613',
    'gpt-3.5-turbo-16k-0613',
    'gpt-3.5-turbo-16k',
    'gpt-3.5-turbo']
    name: str = "gpt-3.5-turbo-16k"
    
    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        list_of_msg_dicts = [message.dict(include=message_properties) for message in messages]
        formatted_messages = [
            {key: value for key, value in m.items() if value is not None}
            for m in list_of_msg_dicts
        ]
        return formatted_messages
    
    def predict(self, messages: List[IMessage], 
        temperature=0.7, 
        max_tokens=256, 
        enable_json=False, 
        stop: List[str] = None):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        
        Returns:
        - The generated message content.
        """
        formatted_messages = self._format_messages(messages)
        client = OpenAI(api_key=self.api_key)
        
        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content