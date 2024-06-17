import json
from typing import List
from openai import OpenAI
from swarmauri.standard.models.base.LLMBase import LLMBase

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

    
    def predict(self, messages, temperature=0.7, max_tokens=256, enable_json=False, stop: List[str] = None):
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
        client = OpenAI(api_key=self.api_key)
        
        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=messages,
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
                messages=messages,
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