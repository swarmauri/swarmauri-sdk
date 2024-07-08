import logging
import json
from typing import List, Literal, Dict, Any
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GeminiSchemaConverter import GeminiSchemaConverter
import google.generativeai as genai

class GeminiToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"
    type: Literal['GeminiToolModel'] = 'GeminiToolModel'

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GeminiSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages


    def predict(self, 
        conversation, 
        toolkit=None, 
        temperature=0.7, 
        max_tokens=256):
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

        client = genai.GenerativeModel(model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config)



        formatted_messages = self._format_messages(conversation.history)
        logging.info(f'formatted_messages: {formatted_messages}')

        response = client.generate_content(
            formatted_messages[-1]['content'],
            tools=self._schema_convert_tools(toolkit.tools),
        )
        logging.info(f'response.text: {response.text}')
        conversation.add_message(AgentMessage(content=response.text))

        logging.info(f'conversation: {conversation}')
        return conversation
