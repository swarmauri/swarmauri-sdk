import json
from typing import List, Literal, Dict
import google.generativeai as genai
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GeminiSchemaConverter import GeminiSchemaConverter
import google.generativeai as genai

class GeminiToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"
    type: Literal['GeminiToolModel'] = 'GeminiToolModel'

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GeminiSchemaConverter().convert(tool) for tool in tools]

    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        messages: List[IMessage], 
        tools=None, 
        force_single_step = False,
        max_tokens=1024):

        raise NotImplemenetedError('🚧 Placeholder')
