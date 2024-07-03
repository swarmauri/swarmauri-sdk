from groq import Groq
import json
from typing import List, Literal, Dict, Any
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GroqSchemaConverter import GroqSchemaConverter

class GroqToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "gemma-7b-it"
    type: Literal['GroqToolModel'] = 'GroqToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GroqSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        messages: List[IMessage], 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(messages)

        client = Groq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        return response