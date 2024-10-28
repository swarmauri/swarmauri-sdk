import asyncio
import logging
from typing import List, Dict, Any, Literal, AsyncIterator, Iterator, Optional, Union
from pydantic import PrivateAttr
import cohere

from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage, contentItem
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.CohereSchemaConverter import (
    CohereSchemaConverter,
)


class CohereToolModel(LLMBase):
    """
    A model for interacting with Cohere's API for tool-augmented conversations.
    Provider resources: https://docs.cohere.com/docs/models#command
    """

    api_key: str
    _client: Optional[cohere.Client] = PrivateAttr(default=None)
    allowed_models: List[str] = [
        "command-r",
        "command-r-plus",
        "command-r-plus-08-2024",
    ]
    name: str = "command-r"
    type: Literal["CohereToolModel"] = "CohereToolModel"
    resource: str = "LLM"

    def __init__(self, **data):
        super().__init__(**data)
        self._client = cohere.Client(api_key=self.api_key)

    def model_dump(self, **kwargs):
        dump = super().model_dump(**kwargs)
        return {k: v for k, v in dump.items() if k != "_client"}

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        if not tools:
            return []
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _extract_text_content(self, content: Union[str, List[contentItem]]) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_contents = [
                item["text"]
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
                and "text" in item
            ]
            return " ".join(text_contents)
        return ""

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        formatted_messages = []
        role_mapping = {
            "human": "User",
            "agent": "Chatbot",
            "system": "System",
            "tool": "Tool",
        }

        for message in messages:
            message_dict = {}

            # Extract content
            if hasattr(message, "content"):
                content = message.content
                message_dict["message"] = self._extract_text_content(content)

            # Map role to Cohere expected roles
            if hasattr(message, "role"):
                original_role = message.role.lower()
                message_dict["role"] = role_mapping.get(
                    original_role, "User"
                )  # Default to User if unknown role

            # Add other properties if they exist
            for prop in ["name", "tool_call_id", "tool_calls"]:
                if hasattr(message, prop):
                    value = getattr(message, prop)
                    if value is not None:
                        message_dict[prop] = value

            formatted_messages.append(message_dict)

        return formatted_messages

    def _ensure_conversation_has_message(self, conversation):
        if not conversation.history:
            conversation.add_message(
                HumanMessage(content=[{"type": "text", "text": "Hello"}])
            )
        return conversation

    def _process_tool_calls(self, response, toolkit):
        tool_results = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                logging.info(f"Processing tool call: {tool_call}")
                func_name = tool_call.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.parameters
                func_results = func_call(**func_args)
                tool_results.append(
                    {"call": tool_call, "outputs": [{"result": func_results}]}
                )
            logging.info(f"Tool results: {tool_results}")
        return tool_results

    def predict(self, conversation, toolkit=None, temperature=0.3, max_tokens=1024):
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        tool_response = self._client.chat(
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            force_single_step=True,
            tools=tools,
        )

        tool_results = self._process_tool_calls(tool_response, toolkit)

        agent_response = self._client.chat(
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature,
        )

        conversation.add_message(AgentMessage(content=agent_response.text))
        return conversation

    def stream(
        self, conversation, toolkit=None, temperature=0.3, max_tokens=1024
    ) -> Iterator[str]:
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        tool_response = self._client.chat(
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            force_single_step=True,
            tools=tools,
        )

        tool_results = self._process_tool_calls(tool_response, toolkit)

        stream = self._client.chat_stream(
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature,
        )

        collected_content = []
        for chunk in stream:
            if hasattr(chunk, "text"):
                collected_content.append(chunk.text)
                yield chunk.text

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self, conversations: List, toolkit=None, temperature=0.3, max_tokens=1024
    ) -> List:
        results = []
        for conv in conversations:
            result = self.predict(
                conversation=conv,
                toolkit=toolkit,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            results.append(result)
        return results

    async def apredict(
        self, conversation, toolkit=None, temperature=0.3, max_tokens=1024
    ):
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        tool_response = await asyncio.to_thread(
            self._client.chat,
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            force_single_step=True,
            tools=tools,
        )

        tool_results = self._process_tool_calls(tool_response, toolkit)

        agent_response = await asyncio.to_thread(
            self._client.chat,
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature,
        )

        conversation.add_message(AgentMessage(content=agent_response.text))
        return conversation

    async def astream(
        self, conversation, toolkit=None, temperature=0.3, max_tokens=1024
    ) -> AsyncIterator[str]:
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        tool_response = await asyncio.to_thread(
            self._client.chat,
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            force_single_step=True,
            tools=tools,
        )

        tool_results = self._process_tool_calls(tool_response, toolkit)

        stream = await asyncio.to_thread(
            self._client.chat_stream,
            model=self.name,
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature,
        )

        collected_content = []
        for chunk in stream:
            if hasattr(chunk, "text"):
                collected_content.append(chunk.text)
                yield chunk.text
            await asyncio.sleep(0)

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def abatch(
        self,
        conversations: List,
        toolkit=None,
        temperature=0.3,
        max_tokens=1024,
        max_concurrent=5,
    ) -> List:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
