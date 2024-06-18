import json
from typing import List
import google.generativeai as genai
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class GeminiProModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"

    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ['content', 'role']
        sanitized_messages = [message.dict(include=message_properties) for message in messages 
            if message['role'] != 'system']

        for message in sanitized_messages:
            if message['role'] == 'assistant':
                message['role'] = 'model'

            # update content naming
            message['parts'] = message['content']

        return sanitized_messages

    def _get_system_context(self, messages:List[IMessage]) -> str:
        system_context = None
        for message in messages:
            if message.role == 'system':
                system_context = message.content
        return system_context
    
    def predict(self, messages, temperature=0.7, max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
            }

        safety_settings = [
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


        system_context = self._get_system_context(messages)
        formatted_messages = self._format_messages(messages)


        next_message = formatted_messages.pop()

        client = genai.GenerativeModel(model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_context)

        convo = client.start_chat(
            history=formatted_messages,
            )

        convo.send_message(next_message['parts'])

        message_content = convo.last.text
        
        return message_content
