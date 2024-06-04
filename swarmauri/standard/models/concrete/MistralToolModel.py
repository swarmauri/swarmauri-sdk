import json
from typing import List
from dataclasses import dataclass
from mistralai.client import MistralClient
from swarmauri.standard.models.base.ModelBase import ModelBase

class MistralModel(ModelBase):
    allowed_models = ['open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-large-latest',
    ]
    api_key: str = ""
    model_name: str = "open-mixtral-8x22b"

    def __post_init__(self):
        self._validate_model_name()
        self.client =  MistralClient(api_key=api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")
        

    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, 
        max_tokens=1024, safe_prompt: bool = False):

        if tools and not tool_choice:
            tool_choice = "auto"
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            safe_prompt=safe_prompt
        )
        return response