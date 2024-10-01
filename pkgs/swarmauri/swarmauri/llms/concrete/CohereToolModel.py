import logging
import json
from typing import List, Literal
from typing import List, Dict, Any, Literal
import cohere
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.CohereSchemaConverter import (
    CohereSchemaConverter,
)


class CohereToolModel(LLMBase):
    """
    Provider resources: https://docs.cohere.com/docs/models#command
    """

    api_key: str
    allowed_models: List[str] = [
        "command-r",
        "command-r-08-2024",
        "command-r-plus",
        "command-r-plus-08-2024",
        "command",
        "command-light",
    ]
    name: str = "command-r"
    type: Literal["CohereToolModel"] = "CohereToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(self, conversation, toolkit=None, temperature=0.3, max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = cohere.Client(api_key=self.api_key)
        preamble = ""  # 🚧  Placeholder for implementation logic

        logging.info(
            f"_schema_convert_tools: {self._schema_convert_tools(toolkit.tools)}"
        )
        logging.info(f"message: {formatted_messages[-1]}")
        logging.info(f"formatted_messages: {formatted_messages}")

        tool_response = client.chat(
            model=self.name,
            message=formatted_messages[-1]["content"],
            chat_history=formatted_messages[:-1],
            force_single_step=True,
            tools=self._schema_convert_tools(toolkit.tools),
        )

        logging.info(f"tool_response: {tool_response}")
        logging.info(tool_response.text)
        tool_results = []
        for tool_call in tool_response.tool_calls:
            logging.info(f"tool_call: {tool_call}")
            func_name = tool_call.name
            func_call = toolkit.get_tool_by_name(func_name)
            func_args = tool_call.parameters
            func_results = func_call(**func_args)
            tool_results.append(
                {"call": tool_call, "outputs": [{"result": func_results}]}
            )  # 🚧 Placeholder for variable key-names

        logging.info(f"tool_results: {tool_results}")
        agent_response = client.chat(
            model=self.name,
            message=formatted_messages[-1]["content"],
            chat_history=formatted_messages[:-1],
            tools=self._schema_convert_tools(toolkit.tools),
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature,
        )

        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f"conversation: {conversation}")
        return conversation
