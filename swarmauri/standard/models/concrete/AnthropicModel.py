import json
from typing import List
import anthropic
from swarmauri.core.models.IPredict import IPredict
from swarmauri.standard.models.base.ModelBase import ModelBase


class AnthropicModel(ModelBase, IPredict):
    allowed_models = ['claude-3-opus-20240229', 
    'claude-3-sonnet-20240229', 
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
    'claude-instant-1.2']

    def __init__(self, api_key: str, model_name: str = 'claude-3-haiku-20240307'):
        if model_name not in self.allowed_models:
            raise ValueError(f"Model name '{model_name}' is not supported. Choose from {self.allowed_models}")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        super().__init__(model_name)
        
    
    def predict(self, messages, temperature=0.7, max_tokens=256):



        # Get system_context
        system_context = None
        for message in messages:
            if message['role'] == 'system':
                system_context = message['content']

        # Remove system instruction from messages
        sanitized_messages = [message for message in messages if message['role'] != 'system'] 

        # we should only remove one message for system instruction
        if len(sanitized_messages) + 1 > len(messages):
            raise ValueError('cannot send an array of conversations containing more than one system instruction.')

        # Chat
        response = self.client.messages.create(
            model=self.model_name,
            messages=sanitized_messages,
            system=system_context,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        
        message_content = response.content[0].text
        return message_content