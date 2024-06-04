import json
from typing import List
from dataclasses import dataclass
from groq import Groq
from swarmauri.standard.models.base.ModelBase import ModelBase

@dataclass
class GroqModel(ModelBase):
    allowed_models = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    api_key: str = ""
    model_name: str = "mixtral-8x7b-32768"

    def __post_init__(self):
        self._validate_model_name()
        self.client = Groq(api_key=self.api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")
    
    def predict(self, messages, 
        temperature=0.7, 
        max_tokens=256, 
        top_p=1, 
        enable_json=False, 
        stop: List[str] = None):
    
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=top_p,
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
                top_p=top_p,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content