import json
from typing import List
from dataclasses import dataclass
import cohere
from swarmauri.standard.models.base.ModelBase import ModelBase

@dataclass
class CohereModel(ModelBase):
    allowed_models = ['command-light',
    'command', 
    'command-r',
    'command-r-plus']
    api_key: str = ""
    model_name: str = "command-light"

    def __post_init__(self):
        self._validate_model_name()
        self.client = cohere.Client(api_key=self.api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")

    
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