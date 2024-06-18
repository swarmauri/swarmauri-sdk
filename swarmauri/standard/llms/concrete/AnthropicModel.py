import json
from typing import List
import anthropic
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class AnthropicModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['claude-3-opus-20240229', 
    'claude-3-sonnet-20240229', 
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
    'claude-instant-1.2']
    name: str = "claude-3-haiku-20240307"

    
    def predict(self, messages: List[IMessage], 
        temperature=0.7, 
        max_tokens=256):
        # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        messages = [message.dict(include=message_properties) for message in messages if message.role != 'tool']

        # Create client
        client = anthropic.Anthropic(api_key=self.api_key)
        
        # Get system_context from last message with system context in it
        system_context = None
        for message in messages:
            if message['role'] == 'system':
                system_context = message['content']

        
        # Remove system instruction from messages
        sanitized_messages = [message for message in messages if message['role'] != 'system']

        if system_context:
            response = client.messages.create(
                model=self.name,
                messages=sanitized_messages,
                system=system_context,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            response = client.messages.create(
                model=self.name,
                messages=sanitized_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        message_content = response.content[0].text
        return message_content
