import json
from typing import List
import cohere
from swarmauri.core.models.IPredict import IPredict
from swarmauri.standard.models.base.ModelBase import ModelBase


class CohereModel(ModelBase, IPredict):
    allowed_models = ['command-light',
    'command', 
    'command-r',
    'command-r-plus']

    def __init__(self, api_key: str, model_name: str = 'command-light'):
        if model_name not in self.allowed_models:
            raise ValueError(f"Model name '{model_name}' is not supported. Choose from {self.allowed_models}")
        
        self.client = cohere.Client(api_key=api_key)
        super().__init__(model_name)
        
    
    def predict(self, messages, temperature=0.7, max_tokens=256):
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_truncation='OFF',
            connectors=[]
        )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content