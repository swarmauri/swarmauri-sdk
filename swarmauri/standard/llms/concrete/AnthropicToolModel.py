import json
from typing import List, Dict, Literal, Any
import logging
import anthropic
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.AnthropicSchemaConverter import AnthropicSchemaConverter

class AnthropicToolModel(LLMBase):
    """
    Provider resources: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    """
    api_key: str
    allowed_models: List[str] = ['claude-3-haiku-20240307',
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229']
    name: str = "claude-3-haiku-20240307"
    type: Literal['AnthropicToolModel'] = 'AnthropicToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        schema_result = [AnthropicSchemaConverter().convert(tools[tool]) for tool in tools]
        logging.info(schema_result)
        return schema_result

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = anthropic.Anthropic(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = {"type":"auto"}

        tool_response = client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.content[0].text] 
        tool_calls = tool_response.content[0].text

        logging.info(f"tool_calls: {tool_calls}")

        if tool_calls:
            func_name = tool_response.content[1].name
            
            func_call = toolkit.get_tool_by_name(func_name)
            func_args = tool_response.content[1].input
            func_result = func_call(**func_args)
            
        logging.info(f"messages: {messages}")

        agent_response = f"{tool_calls} {func_result}"
        agent_message = AgentMessage(content=agent_response)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation