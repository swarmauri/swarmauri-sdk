import json
from typing import List
from openai import OpenAI
from swarmauri.core.models.IPredict import IPredict
from swarmauri.standard.models.base.ModelBase import ModelBase


class OpenAIModel(ModelBase, IPredict):
    allowed_models = ['gpt-4o', 
    'gpt-4-turbo', 
    'gpt-4-0125-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-4-32k',
    'gpt-4-32k-0613',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-16k',
    'gpt-3.5-turbo']

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the OpenAI model with an API key.

        Parameters:
        - api_key (str): Your OpenAI API key.
        """
        if model_name not in self.allowed_models:
            raise ValueError(f"Model name '{model_name}' is not supported. Choose from {self.allowed_models}")
        
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)
        
    
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
        
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
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
            response = self.client.chat.completions.create(
                model=self.model_name,
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