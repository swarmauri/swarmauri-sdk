from typing import List, Literal, Dict, Any
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.OpenAISchemaConverter import OpenAISchemaConverter

class OpenAIToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613']
    name: str = "gpt-3.5-turbo-0125"
    type: Literal['OpenAIToolModel'] = 'OpenAIToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [OpenAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = OpenAI(api_key=self.api_key)
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