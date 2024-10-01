import json
import logging
from typing import List, Literal, Dict, Any
from openai import OpenAI
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)


class OpenAIToolModel(LLMBase):
    """
    Provider resources: https://platform.openai.com/docs/guides/function-calling/which-models-support-function-calling
    """

    api_key: str
    allowed_models: List[str] = [
        "gpt-4o",
        "gpt-4o-2024-05-13",
        "gpt-4-turbo",
        "gpt-4o-mini",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-turbo-preview",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-4-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0613",
    ]
    name: str = "gpt-3.5-turbo-0125"
    type: Literal["OpenAIToolModel"] = "OpenAIToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [OpenAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ):
        formatted_messages = self._format_messages(conversation.history)

        client = OpenAI(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(f"tool_response: {tool_response}")
        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        logging.info(f"messages: {messages}")
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation
