import json
import logging
from typing import List, Literal, Dict, Any
from mistralai import Mistral
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.MistralSchemaConverter import (
    MistralSchemaConverter,
)


class MistralToolModel(LLMBase):
    """
    Provider resources: https://docs.mistral.ai/capabilities/function_calling/#available-models
    """

    api_key: str
    allowed_models: List[str] = [
        "open-mixtral-8x22b",
        "mistral-small-latest",
        "mistral-large-latest",
        "open-mistral-nemo",
    ]
    name: str = "open-mixtral-8x22b"
    type: Literal["MistralToolModel"] = "MistralToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [MistralSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "tool_call_id"]
        # message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
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
        safe_prompt: bool = False,
    ):
        client = Mistral(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.complete(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt,
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)

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

        agent_response = client.chat.complete(model=self.name, messages=messages)
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation
