import json
from typing import List, Dict, Literal, Any
import anthropic
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.AnthropicSchemaConverter import AnthropicSchemaConverter

class AnthropicToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['']
    name: str = "command-light"
    type: Literal['AnthropicToolModel'] = 'AnthropicToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [AnthropicSchemaConverter().convert(tool) for tool in tools]

    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        messages: List[IMessage], 
        tools=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(messages)

        client = anthropic.Anthropic(api_key=self.api_key)
        if tools and not tool_choice:
            tool_choice = "auto"

        response = client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(tools),
            tool_choice=tool_choice,
        )
        return response