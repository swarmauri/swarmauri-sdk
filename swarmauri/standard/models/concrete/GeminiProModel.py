import json
from typing import List
import google.generativeai as genai
from swarmauri.core.models.IPredict import IPredict
from swarmauri.standard.models.base.ModelBase import ModelBase


class GeminiProModel(ModelBase, IPredict):
    allowed_models = ['gemini-1.5-pro-latest']

    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-pro-latest'):
        if model_name not in self.allowed_models:
            raise ValueError(f"Model name '{model_name}' is not supported. Choose from {self.allowed_models}")
        
        genai.configure(api_key=api_key)
        self.safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
        ]
        self.safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
        ]
        self.client = None
        super().__init__(model_name)
        
    
    def predict(self, messages, temperature=0.7, max_tokens=256):
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
            }

        system_context = None
        for message in messages:

            # update role naming
            role = message.pop('role')
            if role == 'assistant':
                role = 'model'

            if role == 'system':
                system_context = message['content']

            # rename role
            message['role'] = role

            # update content naming
            message['parts'] = message.pop('content')

        
        # Remove system instruction from messages
        sanitized_messages = [message for message in messages if message['role'] != 'system'] 

        # if we remove more than one system message from the array
        # then we know we were given too many system messages
        # we raise an error in this scenario.
        # Examples:
        # 10 - 1 = 9 so if 9 + 1 < 10  then negative is good
        # 10 - 2 = 8, so if 8 + 1 < 10 then positive is bad
        if len(sanitized_messages) + 1 > len(messages):
            raise ValueError('cannot send an array of conversations containing more than one system instruction.')


        next_message = sanitized_messages.pop()

        self.client = genai.GenerativeModel(model_name=self.model_name,
            safety_settings=self.safety_settings,
            generation_config=generation_config)

        convo = self.client.start_chat(
            history=sanitized_messages,
            )

        convo.send_message(next_message['parts'])

        message_content = convo.last.text
        
        return message_content
