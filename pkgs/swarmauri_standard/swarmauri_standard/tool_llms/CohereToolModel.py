import asyncio
import json
import logging
import uuid
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type, Union

import httpx
from pydantic import PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.conversations.IConversation import IConversation

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage, contentItem
from swarmauri_standard.schema_converters.CohereSchemaConverter import (
    CohereSchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.duration_manager import DurationManager
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "CohereToolModel")
class CohereToolModel(ToolLLMBase):
    """
    A language model implementation for interacting with Cohere's API, specifically designed for\
    tool-augmented conversations.

    This class provides both synchronous and asynchronous methods for generating responses,
    handling tool calls, and managing conversations with the Cohere API. It supports streaming
    responses and batch processing of multiple conversations.

    Attributes:
        api_key (str): The API key for authenticating with Cohere's API
        allowed_models (List[str]): List of supported Cohere model names
        name (str): The default model name to use
        type (Literal["CohereToolModel"]): The type identifier for this model
        resource (str): The resource type identifier

    Link to Allowed Models: https://docs.cohere.com/docs/models#command
    Link to API Key: https://dashboard.cohere.com/api-keys
    """

    BASE_URL: str = "https://api.cohere.ai/v1"
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()
    api_key: SecretStr
    allowed_models: List[str] = [
        "command-a-03-2025",
        "command-r7b-12-2024",
        "command-r-plus",
        "command-r",
        "command",
        "command-nightly",
        "command-light",
        "command-light-nightly",
    ]
    name: str = "command-a-03-2025"

    type: Literal["CohereToolModel"] = "CohereToolModel"

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Initialize the CohereToolModel with the provided configuration.

        Args:
            **data (Dict[str, Any]): Keyword arguments for configuring the model, including api_key
        """
        super().__init__(**data)
        self._headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key.get_secret_value()}",
        }
        self._client = httpx.Client(
            headers=self._headers, base_url=self.BASE_URL, timeout=self.timeout
        )
        self._async_client = httpx.AsyncClient(
            headers=self._headers, base_url=self.BASE_URL, timeout=self.timeout
        )

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Get the schema converter class for this tool model.

        Returns:
            Type[SchemaConverterBase]: The CohereSchemaConverter class
        """
        return CohereSchemaConverter

    def _schema_convert_tools(
        self, tools: Dict[str, SubclassUnion[ToolBase]]
    ) -> List[Dict[str, Any]]:
        """
        Convert tool definitions to Cohere's expected schema format.

        Args:
            tools: Dictionary of tools to convert

        Returns:
            List[Dict[str, Any]]: List of converted tool definitions
        """
        if not tools:
            return []
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _extract_text_content(self, content: Union[str, List[contentItem]]) -> str:
        """
        Extract text content from either a string or a list of content items.

        Args:
            content (Union[str, List[contentItem]]): The content to extract text from

        Returns:
            str: The extracted text content
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
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Format messages into Cohere's expected chat format.

        Args:
            messages (List[Type[MessageBase]]): List of messages to format

        Returns:
            List[Dict[str, str]]: Formatted messages for Cohere's API
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
            if hasattr(message, "content"):
                content = message.content
                message_dict["message"] = self._extract_text_content(content)

            if hasattr(message, "role"):
                original_role = message.role.lower()
                message_dict["role"] = role_mapping.get(original_role, "User")

            for prop in ["name", "tool_call_id", "tool_calls"]:
                if hasattr(message, prop):
                    value = getattr(message, prop)
                    if value is not None:
                        message_dict[prop] = value

            formatted_messages.append(message_dict)

        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data: Dict[str, Any],
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
    ) -> UsageData:
        """
        Prepare usage statistics from API response and timing data.

        Args:
            usage_data (Dict[str, Any]): Dictionary containing token usage information from the API
            prompt_time (float): Time taken to send the prompt
            completion_time (float): Time taken to receive the completion

        Returns:
            UsageData: Object containing formatted usage statistics
        """
        total_time = prompt_time + completion_time

        input_tokens = usage_data.get("input_tokens", 0)
        output_tokens = usage_data.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens

        usage = UsageData(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=total_tokens,
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )
        return usage

    def _ensure_conversation_has_message(
        self, conversation: Conversation
    ) -> Conversation:
        """
        Ensure that a conversation has at least one message by adding a default message if empty.

        Args:
            conversation (Conversation): The conversation to check

        Returns:
            Conversation: The conversation, potentially with an added default message
        """
        if not conversation.history:
            conversation.add_message(
                HumanMessage(content=[{"type": "text", "text": "Hello"}])
            )
        return conversation

    def _process_tool_calls(
        self, response_data: Dict[str, Any], toolkit: Toolkit
    ) -> tuple[List[Dict[str, Any]], List[FunctionMessage]]:
        """
        Process tool calls from the model's response and execute them using the provided toolkit.

        Args:
            response_data (Dict[str, Any]): The response data containing tool calls
            toolkit (Toolkit): The toolkit containing the tools to execute

        Returns:
            tuple[List[Dict[str, Any]], List[FunctionMessage]]: Results of the tool executions and tool messages
        """
        tool_results = []
        tool_calls = response_data.get("tool_calls", [])
        logging.info(f"Tool calls: {tool_calls}")

        tool_messages = []
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.get("name")
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.get("parameters", {})
                func_results = func_call(**func_args)
                tool_results.append(
                    {"call": tool_call, "outputs": [{"result": func_results}]}
                )

                tool_messages.append(
                    FunctionMessage(
                        content=json.dumps(func_results),
                        tool_call_id=str(uuid.uuid4()),
                        name=func_name,
                    )
                )

        return tool_results, tool_messages

    def _prepare_chat_payload(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        tool_results: List[Dict[str, Any]] = None,
        temperature: float = 0.3,
        force_single_step: bool = True,
    ) -> Dict[str, Any]:
        """
        Prepare the payload for a chat request to Cohere's API.

        Args:
            message (str): The current message to process
            chat_history (List[Dict[str, str]]): Previous chat history
            tools (List[Dict[str, Any]], optional): Available tools
            tool_results (List[Dict[str, Any]], optional): Results from previous tool calls
            temperature (float, optional): Sampling temperature
            force_single_step (bool, optional): Whether to force single-step responses

        Returns:
            Dict[str, Any]: The prepared payload for the API request
        """
        payload = {
            "message": message,
            "model": self.name,
            "temperature": temperature,
            "force_single_step": force_single_step,
        }

        if chat_history:
            payload["chat_history"] = chat_history

        if tools:
            payload["tools"] = tools

        if tool_results:
            payload["tool_results"] = tool_results

        return payload

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Generate a response for a conversation synchronously.

        Args:
            conversation (Conversation): The conversation to generate a response for
            toolkit (Toolkit): Toolkit containing available tools
            multiturn (bool, optional): Whether to use multi-turn conversation. Defaults to True
            temperature (float, optional): Sampling temperature. Defaults to 0.7
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024

        Returns:
            IConversation: The updated conversation with the model's response
        """
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        with DurationManager() as tool_timer:
            tool_payload = self._prepare_chat_payload(
                message=formatted_messages[-1]["message"],
                chat_history=(
                    formatted_messages[:-1] if len(formatted_messages) > 1 else None
                ),
                tools=tools,
                force_single_step=True,
            )

            tool_response = self._client.post("/chat", json=tool_payload)
            logging.info(tool_response.json())
            tool_response.raise_for_status()
            tool_data = tool_response.json()

        tool_results, tool_messages = self._process_tool_calls(tool_data, toolkit)

        conversation.add_messages(tool_messages)

        if multiturn:
            with DurationManager() as response_timer:
                response_payload = self._prepare_chat_payload(
                    message=formatted_messages[-1]["message"],
                    chat_history=(
                        formatted_messages[:-1] if len(formatted_messages) > 1 else None
                    ),
                    tools=tools,
                    tool_results=tool_results,
                    temperature=temperature,
                    force_single_step=True,
                )

                response = self._client.post("/chat", json=response_payload)
                response.raise_for_status()
                response_data = response.json()

                usage_data = response_data.get("usage", {})

            usage = self._prepare_usage_data(
                usage_data, tool_timer.duration, response_timer.duration
            )

            conversation.add_message(
                AgentMessage(content=response_data.get("text", ""), usage=usage)
            )
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """
        Stream a response for a conversation synchronously.

        Args:
            conversation (Conversation): The conversation to generate a response for
            toolkit (Toolkit): Toolkit containing available tools
            temperature (float, optional): Sampling temperature. Defaults to 0.3
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024

        Returns:
            Iterator[str]: An iterator yielding response chunks
        """
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        # Handle tool call first
        tool_payload = self._prepare_chat_payload(
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
        )
        with DurationManager() as prompt_timer:
            tool_response = self._client.post("/chat", json=tool_payload)
            tool_response.raise_for_status()
            tool_data = tool_response.json()

        tool_results, tool_messages = self._process_tool_calls(tool_data, toolkit)

        conversation.add_messages(tool_messages)

        # Prepare streaming payload
        stream_payload = self._prepare_chat_payload(
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            tool_results=tool_results,
            temperature=temperature,
            force_single_step=True,
        )
        stream_payload["stream"] = True

        collected_content = []
        usage_data = {}
        with DurationManager() as completion_timer:
            with self._client.stream("POST", "/chat", json=stream_payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "text" in chunk:
                            content = chunk["text"]
                            collected_content.append(content)
                            yield content
                        elif "usage" in chunk:
                            usage_data = chunk["usage"]

        full_content = "".join(collected_content)
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=full_content), usage=usage)

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        multiturn: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Generate a response for a conversation asynchronously.

        Args:
            conversation (Conversation): The conversation to generate a response for
            toolkit (Toolkit): Toolkit containing available tools
            multiturn (bool, optional): Whether to use multi-turn conversation. Defaults to True
            temperature (float, optional): Sampling temperature. Defaults to 0.3
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024

        Returns:
            IConversation: The updated conversation with the model's response
        """
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        with DurationManager() as tool_timer:
            tool_payload = self._prepare_chat_payload(
                message=formatted_messages[-1]["message"],
                chat_history=(
                    formatted_messages[:-1] if len(formatted_messages) > 1 else None
                ),
                tools=tools,
                force_single_step=True,
            )

            tool_response = await self._async_client.post("/chat", json=tool_payload)
            tool_response.raise_for_status()
            tool_data = tool_response.json()

        tool_results, tool_messages = self._process_tool_calls(tool_data, toolkit)

        conversation.add_messages(tool_messages)

        if multiturn:
            with DurationManager() as response_timer:
                response_payload = self._prepare_chat_payload(
                    message=formatted_messages[-1]["message"],
                    chat_history=(
                        formatted_messages[:-1] if len(formatted_messages) > 1 else None
                    ),
                    tools=tools,
                    tool_results=tool_results,
                    temperature=temperature,
                    force_single_step=True,
                )

                response = await self._async_client.post("/chat", json=response_payload)
                response.raise_for_status()
                response_data = response.json()

                usage_data = response_data.get("usage", {})

            usage = self._prepare_usage_data(
                usage_data, tool_timer.duration, response_timer.duration
            )

            conversation.add_message(
                AgentMessage(content=response_data.get("text", ""), usage=usage)
            )
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Stream a response for a conversation asynchronously.

        Args:
            conversation (Conversation): The conversation to generate a response for
            toolkit (Toolkit): Toolkit containing available tools
            temperature (float, optional): Sampling temperature. Defaults to 0.3
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024

        Returns:
            AsyncIterator[str]: An async iterator yielding response chunks
        """
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        # Handle tool call first
        tool_payload = self._prepare_chat_payload(
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
        )
        with DurationManager() as prompt_timer:
            tool_response = await self._async_client.post("/chat", json=tool_payload)
            tool_response.raise_for_status()
            tool_data = tool_response.json()

        tool_results, tool_messages = self._process_tool_calls(tool_data, toolkit)

        conversation.add_messages(tool_messages)

        # Prepare streaming payload
        stream_payload = self._prepare_chat_payload(
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            tool_results=tool_results,
            temperature=temperature,
            force_single_step=True,
        )
        stream_payload["stream"] = True

        collected_content = []
        usage_data = {}

        async with self._async_client.stream(
            "POST", "/chat", json=stream_payload
        ) as response:
            response.raise_for_status()
            with DurationManager() as completion_timer:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "text" in chunk:
                                content = chunk["text"]
                                collected_content.append(content)
                                yield content
                            elif "usage" in chunk:
                                usage_data = chunk["usage"]
                        except json.JSONDecodeError:
                            continue

        full_content = "".join(collected_content)
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=full_content), usage=usage)

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> List[IConversation]:
        """
        Process multiple conversations in batch mode synchronously.

        This method takes a list of conversations and processes them sequentially using
        the predict method. Each conversation is processed independently with the same
        parameters.

        Args:
            conversations (List[Conversation]): A list of conversation objects to process
            toolkit (Toolkit): The toolkit containing available tools for the model
            temperature (float, optional): The sampling temperature for response generation.
                Defaults to 0.3
            max_tokens (int, optional): The maximum number of tokens to generate for each
                response. Defaults to 1024

        Returns:
            List[IConversation]: A list of processed conversations with their respective responses
        """
        return [
            self.predict(
                conv, toolkit=toolkit, temperature=temperature, max_tokens=max_tokens
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_concurrent: int = 5,
    ) -> List[IConversation]:
        """
        Process multiple conversations in batch mode asynchronously.

        This method processes multiple conversations concurrently while limiting the
        maximum number of simultaneous requests using a semaphore. This helps prevent
        overwhelming the API service while still maintaining efficient processing.

        Args:
            conversations (List[Conversation]): A list of conversation objects to process
            toolkit (Toolkit): The toolkit containing available tools for the model
            temperature (float, optional): The sampling temperature for response generation.
                Defaults to 0.7
            max_tokens (int, optional): The maximum number of tokens to generate for each
                response. Defaults to 1024
            max_concurrent (int, optional): The maximum number of conversations to process
                simultaneously. Defaults to 5

        Returns:
            List[IConversation]: A list of processed conversations with their respective responses

        Note:
            The max_concurrent parameter helps control API usage and prevent rate limiting
            while still allowing for parallel processing of multiple conversations.
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

    def get_allowed_models(self) -> List[str]:
        """
        Query the LLMProvider API endpoint to get the list of allowed models.

        Returns:
            List[str]: List of allowed model names from the API
        """
        non_tool_models = ["c4ai-aya-expanse-32b", "command-light-nightly", "command"]
        response = self._client.get("/models")
        response.raise_for_status()
        models_data = response.json()

        return [
            model["name"]
            for model in models_data["models"]
            if "chat" in model["endpoints"]
            and "generate" in model["endpoints"]
            and model["name"] not in non_tool_models
        ]
