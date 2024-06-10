import json
from typing import List
from dataclasses import dataclass
from mistralai.client import MistralClient
from swarmauri.standard.models.base.ModelBase import ModelBase

class MistralModel(ModelBase):
    allowed_models = ['open-mistral-7b', 
    'open-mixtral-8x7b', 
    'open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-medium-latest',
    'mistral-large-latest',
    'codestral'
    ]
    api_key: str = ""
    model_name: str = "open-mixtral-8x7b"

    def __post_init__(self):
        self._validate_model_name()
        self.client =  MistralClient(api_key=self.api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")


    def predict(self, messages, 
        temperature: int = 0.7, 
        max_tokens: int = 256, 
        top_p: int = 1,
        enable_json: bool=False, 
        safe_prompt: bool=False):
        
        if enable_json:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt
            )
        else:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,                
                safe_prompt=safe_prompt
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content