import json
from typing import List, Literal, Dict, Any
from mistralai.client import MistralClient
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.MistralSchemaConverter import MistralSchemaConverter

class MistralToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-large-latest',
    ]
    name: str = "open-mixtral-8x22b"
    type: Literal['MistralToolModel'] = 'MistralToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [MistralSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    
    def predict(self, 
        messages: List[IMessage], 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024, 
        safe_prompt: bool = False):

        client =  MistralClient(api_key=self.api_key)
        formatted_messages = self._format_messages(messages)

        if tools and not tool_choice:
            tool_choice = "auto"
            
        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt
        )
        return response