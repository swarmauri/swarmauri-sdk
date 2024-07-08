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
        # Remove system instruction from messages
        message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        sanitized_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages 
            if message.role != 'system']

        for message in sanitized_messages:
            if message['role'] == 'assistant':
                message['role'] = 'model'

            if message['role'] == 'tool':
                message['role'] == 'user'

            # update content naming
            message['parts'] = message.pop('content')

        return sanitized_messages

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

        tool_response = client.generate_content(
            formatted_messages,
            tools=self._schema_convert_tools(toolkit.tools),
        )
        logging.info(f'tool_response: {tool_response}')

        tool_calls = tool_response.candidates[0]['content']['parts']
        for tool_call in tool_calls:
            func_name = tool_call['name']
            func_args = tool_call['args']
            func_call = toolkit.get_tool_by_name(func_name)
            func_result = func_call(**func_args)

        formatted_messages.append({"role":"user", "parts": func_result})
        agent_response = client.generate_content(
            formatted_messages,
            tools=self._schema_convert_tools(toolkit.tools),
        )

        logging.info(f'agent_response: {agent_response}')
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f'conversation: {conversation}')
        return conversation
