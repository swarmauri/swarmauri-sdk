import json
from typing import List
from dataclasses import dataclass
import anthropic
from swarmauri.standard.models.base.ModelBase import ModelBase

@dataclass
class AnthropicModel(BaseLLM):
    allowed_models = ['claude-3-opus-20240229', 
    'claude-3-sonnet-20240229', 
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
    'claude-instant-1.2']
    api_key: str = ""
    model_name: str = "claude-3-haiku-20240307"

    def __post_init__(self):
        self._validate_model_name()
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")

    
    def predict(self, messages, temperature=0.7, max_tokens=256):

        # Get system_context from last message with system context in it
        system_context = None
        for message in messages:
            if message['role'] == 'system':
                system_context = message['content']

        
        # Remove system instruction from messages
        sanitized_messages = [message for message in messages if message['role'] != 'system']

        if system_context:
            response = self.client.messages.create(
                model=self.model_name,
                messages=sanitized_messages,
                system=system_context,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            response = self.client.messages.create(
                model=self.model_name,
                messages=sanitized_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        message_content = response.content[0].text
        return message_content
