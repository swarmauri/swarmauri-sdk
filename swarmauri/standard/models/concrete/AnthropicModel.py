import json
from typing import List
import anthropic
import logging
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

        # Get system_context from last message with system context in it
        system_context = None
        for message in messages:
            if message['role'] == 'system':
                system_context = message['content']
                logging.info(f'Setting system to {system_context}.')

        
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