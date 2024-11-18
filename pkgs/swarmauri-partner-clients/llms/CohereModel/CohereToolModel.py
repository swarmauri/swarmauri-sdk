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
    This class facilitates the integration with Cohere's conversational models
    and supports both synchronous and asynchronous operations.

    Attributes:
        api_key (str): API key for authenticating with Cohere's API.
        _client (Optional[cohere.Client]): Internal client for Cohere's API.
        allowed_models (List[str]): List of supported model names.
        name (str): Name of the Cohere model to be used.
        type (Literal): Type of the model, fixed as 'CohereToolModel'.
        resource (str): Resource type, defaulting to "LLM".

    Link to Allowed Models: https://docs.cohere.com/docs/models#command
    Link to API Key: https://dashboard.cohere.com/api-keys
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
        """
        Initializes a CohereToolModel instance with provided configuration.

        Args:
            **data: Keyword arguments for initialization, including API key.
        """
        super().__init__(**data)
        self._client = cohere.Client(api_key=self.api_key)

    def model_dump(self, **kwargs):
        """
        Dumps the model's data excluding the internal client for safe serialization.

        Args:
            **kwargs: Additional arguments for the dump method.

        Returns:
            Dict: A dictionary representation of the model's data.
        """
        dump = super().model_dump(**kwargs)
        return {k: v for k, v in dump.items() if k != "_client"}

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        """
        Converts tool specifications using the Cohere schema converter.

        Args:
            tools: A dictionary of tools to be converted.

        Returns:
            List[Dict[str, Any]]: A list of converted tool specifications.
        """
        if not tools:
            return []
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _extract_text_content(self, content: Union[str, List[contentItem]]) -> str:
        """
        Extracts text content from message content items.

        Args:
            content (Union[str, List[contentItem]]): The content to be processed.

        Returns:
            str: Extracted text content.
        """
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
        """
        Formats conversation messages into a structure compatible with Cohere.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of messages to format.

        Returns:
            List[Dict[str, str]]: A formatted list of message dictionaries.
        """
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
        """
        Ensures that a conversation has at least one initial message.

        Args:
            conversation: The conversation object.

        Returns:
            The updated conversation object.
        """
        if not conversation.history:
            conversation.add_message(
                HumanMessage(content=[{"type": "text", "text": "Hello"}])
            )
        return conversation

    def _process_tool_calls(self, response, toolkit):
        """
        Processes tool calls from the Cohere API response.

        Args:
            response: The API response containing tool calls.
            toolkit: The toolkit object with callable tools.

        Returns:
            List[Dict[str, Any]]: List of processed tool call results.
        """
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
        """
        Generates a response from the model for a given conversation.

        Args:
            conversation: The conversation object.
            toolkit: The toolkit object with callable tools (optional).
            temperature (float): The temperature for the model's output.
            max_tokens (int): The maximum number of tokens for the output.

        Returns:
            The updated conversation object with the model's response.
        """
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
        """
        Streams the model's response chunk by chunk for real-time interaction.

        Args:
            conversation: The conversation object.
            toolkit: The toolkit object with callable tools (optional).
            temperature (float): The temperature for the model's output.
            max_tokens (int): The maximum number of tokens for the output.

        Yields:
            str: Chunks of the model's response text.
        """
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
        """
        Processes multiple conversations synchronously in batch mode.

        Args:
            conversations (List): A list of conversation objects to process.
            toolkit (optional): Toolkit object for tool usage.
            temperature (float, optional): Controls response randomness. Defaults to 0.3.
            max_tokens (int, optional): Maximum tokens in each response. Defaults to 1024.

        Returns:
            List: A list of updated conversation objects with responses.
        """
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
        """
        Makes an asynchronous prediction by sending a conversation request to Cohere's API.

        Args:
            conversation: The conversation object to process.
            toolkit (optional): Toolkit object for tool usage.
            temperature (float, optional): Controls response randomness. Defaults to 0.3.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 1024.

        Returns:
            Updated conversation object with the predicted response.
        """
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
        """
        Streams response content asynchronously as it is received from Cohere's API.

        Args:
            conversation: The conversation object to process.
            toolkit (optional): Toolkit object for tool usage.
            temperature (float, optional): Controls response randomness. Defaults to 0.3.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 1024.

        Yields:
            AsyncIterator[str]: Streamed content as it is received.
        """
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
        """
        Processes multiple conversations asynchronously in batch mode with concurrency control.

        Args:
            conversations (List): A list of conversation objects to process.
            toolkit (optional): Toolkit object for tool usage.
            temperature (float, optional): Controls response randomness. Defaults to 0.3.
            max_tokens (int, optional): Maximum tokens in each response. Defaults to 1024.
            max_concurrent (int, optional): Maximum concurrent requests allowed. Defaults to 5.

        Returns:
            List: A list of updated conversation objects with responses.
        """
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
