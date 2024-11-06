import json
import asyncio
import time
from typing import List, Dict, Any, Literal, AsyncIterator, Iterator, Optional, Union
from pydantic import Field
import requests
import aiohttp
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage, UsageData
from swarmauri.messages.concrete.HumanMessage import HumanMessage, contentItem
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.CohereSchemaConverter import (
    CohereSchemaConverter,
)
from swarmauri.utils.duration_manager import DurationManager


class CohereToolModel(LLMBase):
    """
    This class provides synchronous and asynchronous methods to interact with Cohere's language models for text generation,
    as well as methods to process tool calls and conversation history.

    Attributes:
        api_key (str): API key for authenticating with Cohere's API.
        allowed_models (List[str]): A list of models allowed to be used with this tool.
        name (str): The default model name to use.
        type (Literal["CohereToolModel"]): A fixed attribute to identify this class as CohereToolModel.
        resource (str): A string identifier for the resource type, here set as "LLM".
        base_url (str): The base URL for the Cohere API.
        headers (Dict[str, str]): The headers used for HTTP requests, which includes authorization.

    Link to Allowed Models: https://docs.cohere.com/docs/models#command
    Link to API Key: https://dashboard.cohere.com/api-keys

    """

    api_key: str
    allowed_models: List[str] = [
        "command-r",
        "command-r-plus",
        "command-r-plus-08-2024",
    ]
    name: str = "command-r"
    type: Literal["CohereToolModel"] = "CohereToolModel"
    resource: str = "LLM"
    base_url: str = Field(default="https://api.cohere.ai/v1")
    headers: Dict[str, str] = Field(default=None, exclude=True)

    def __init__(self, **data):
        """
        Initializes the CohereToolModel with API key and other configuration settings.

        Args:
            **data: Arbitrary keyword arguments used to initialize the model attributes.
        """
        super().__init__(**data)
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        """
        Converts the toolkit schema into the format required by Cohere's API.

        Args:
            tools: A dictionary containing tool configurations.

        Returns:
            List[Dict[str, Any]]: Converted tool configuration for Cohere's API.
        """
        if not tools:
            return []
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _extract_text_content(self, content: Union[str, List[contentItem]]) -> str:
        """
        Extracts text content from a message content item or list of items.

        Args:
            content (Union[str, List[contentItem]]): A single text item or a list of content items.

        Returns:
            str: Extracted and concatenated text.
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
        Formats messages to match Cohere's expected chat API format.

        Args:
            messages (List[SubclassUnion[MessageBase]]): A list of message objects.

        Returns:
            List[Dict[str, str]]: List of formatted message dictionaries.
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

    def _ensure_conversation_has_message(self, conversation):
        """
        Ensures that a conversation contains at least one message by adding a default if empty.

        Args:
            conversation: The conversation object.

        Returns:
            The modified or original conversation.
        """
        if not conversation.history:
            conversation.add_message(
                HumanMessage(content=[{"type": "text", "text": "Hello"}])
            )
        return conversation

    def _process_tool_calls(self, response_data, toolkit):
        """
        Processes tool calls from response data using the toolkit.

        Args:
            response_data (dict): The response data from Cohere's API.
            toolkit: The toolkit used to process tool calls.

        Returns:
            List[Dict[str, Any]]: List of tool call results.
        """
        tool_results = []
        tool_calls = response_data.get("tool_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.get("name")
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.get("parameters", {})
                func_results = func_call(**func_args)
                tool_results.append(
                    {"call": tool_call, "outputs": [{"result": func_results}]}
                )

        return tool_results

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
        Prepares the payload for a chat request.

        Args:
            message (str): The message to be sent.
            chat_history (List[Dict[str, str]]): The chat history.
            tools (List[Dict[str, Any]], optional): List of tools to be used. Defaults to None.
            tool_results (List[Dict[str, Any]], optional): Tool results from previous calls. Defaults to None.
            temperature (float, optional): Temperature for response randomness. Defaults to 0.3.
            force_single_step (bool, optional): Flag for single-step responses. Defaults to True.

        Returns:
            Dict[str, Any]: The prepared chat payload.
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

    def predict(self, conversation, toolkit=None, temperature=0.3, max_tokens=1024):
        """
        Makes a synchronous prediction by sending a conversation request to Cohere's API.

        Args:
            conversation: The conversation object.
            toolkit (optional): Toolkit object for tool usage.
            temperature (float, optional): Response randomness. Defaults to 0.3.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 1024.

        Returns:
            Updated conversation object with the predicted response.
        """
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        # First chat request for tool calls
        with DurationManager() as tool_timer:
            tool_payload = self._prepare_chat_payload(
                message=formatted_messages[-1]["message"],
                chat_history=(
                    formatted_messages[:-1] if len(formatted_messages) > 1 else None
                ),
                tools=tools,
                force_single_step=True,
            )

            tool_response = requests.post(
                f"{self.base_url}/chat", headers=self.headers, json=tool_payload
            )
            tool_response.raise_for_status()
            tool_data = tool_response.json()

        tool_results = self._process_tool_calls(tool_data, toolkit)

        # Second chat request for final response
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

            response = requests.post(
                f"{self.base_url}/chat", headers=self.headers, json=response_payload
            )
            response.raise_for_status()
            response_data = response.json()

        # Prepare usage data
        usage = UsageData(
            prompt_tokens=response_data.get("usage", {}).get("input_tokens", 0),
            completion_tokens=response_data.get("usage", {}).get("output_tokens", 0),
            total_tokens=response_data.get("usage", {}).get("total_tokens", 0),
            prompt_time=tool_timer.duration,
            completion_time=response_timer.duration,
            total_time=tool_timer.duration + response_timer.duration,
        )

        conversation.add_message(
            AgentMessage(content=response_data.get("text", ""), usage=usage)
        )
        return conversation

    def stream(
        self, conversation, toolkit=None, temperature=0.3, max_tokens=1024
    ) -> Iterator[str]:
        """
        Streams response content as it is received.

        Args:
            conversation: The conversation object.
            toolkit (optional): Toolkit object for tool usage.
            temperature (float, optional): Response randomness. Defaults to 0.3.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 1024.

        Yields:
            Iterator[str]: Streamed content as it is received.
        """
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools) if toolkit else None

        # First chat request for tool calls
        tool_payload = self._prepare_chat_payload(
            message=formatted_messages[-1]["message"],
            chat_history=(
                formatted_messages[:-1] if len(formatted_messages) > 1 else None
            ),
            tools=tools,
            force_single_step=True,
        )

        with requests.post(
            f"{self.base_url}/chat", headers=self.headers, json=tool_payload
        ) as tool_response:
            tool_response.raise_for_status()
            tool_data = tool_response.json()

        tool_results = self._process_tool_calls(tool_data, toolkit)

        # Second chat request with streaming
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

        with requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json=stream_payload,
            stream=True,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if "text" in chunk:
                        content = chunk["text"]
                        collected_content.append(content)
                        yield content
                    elif "usage" in chunk:
                        usage_data = chunk["usage"]

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

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

        async with aiohttp.ClientSession() as session:
            # First chat request for tool calls
            with DurationManager() as tool_timer:
                tool_payload = self._prepare_chat_payload(
                    message=formatted_messages[-1]["message"],
                    chat_history=(
                        formatted_messages[:-1] if len(formatted_messages) > 1 else None
                    ),
                    tools=tools,
                    force_single_step=True,
                )

                async with session.post(
                    f"{self.base_url}/chat", headers=self.headers, json=tool_payload
                ) as tool_response:
                    if tool_response.status != 200:
                        raise Exception(
                            f"API request failed with status {tool_response.status}"
                        )
                    tool_data = await tool_response.json()

            tool_results = self._process_tool_calls(tool_data, toolkit)

            # Second chat request for final response
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

                async with session.post(
                    f"{self.base_url}/chat", headers=self.headers, json=response_payload
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"API request failed with status {response.status}"
                        )
                    response_data = await response.json()

            # Prepare usage data
            usage = UsageData(
                prompt_tokens=response_data.get("usage", {}).get("input_tokens", 0),
                completion_tokens=response_data.get("usage", {}).get(
                    "output_tokens", 0
                ),
                total_tokens=response_data.get("usage", {}).get("total_tokens", 0),
                prompt_time=tool_timer.duration,
                completion_time=response_timer.duration,
                total_time=tool_timer.duration + response_timer.duration,
            )

            conversation.add_message(
                AgentMessage(content=response_data.get("text", ""), usage=usage)
            )
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

        async with aiohttp.ClientSession() as session:
            # First chat request for tool calls
            tool_payload = self._prepare_chat_payload(
                message=formatted_messages[-1]["message"],
                chat_history=(
                    formatted_messages[:-1] if len(formatted_messages) > 1 else None
                ),
                tools=tools,
                force_single_step=True,
            )

            async with session.post(
                f"{self.base_url}/chat", headers=self.headers, json=tool_payload
            ) as tool_response:
                if tool_response.status != 200:
                    raise Exception(
                        f"API request failed with status {tool_response.status}"
                    )
                tool_data = await tool_response.json()

            tool_results = self._process_tool_calls(tool_data, toolkit)

            # Second chat request with streaming
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
            async with session.post(
                f"{self.base_url}/chat", headers=self.headers, json=stream_payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")

                async for line in response.content:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "text" in chunk:
                            content = chunk["text"]
                            collected_content.append(content)
                            yield content
                    await asyncio.sleep(0)

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
        return [
            self.predict(
                conv, toolkit=toolkit, temperature=temperature, max_tokens=max_tokens
            )
            for conv in conversations
        ]

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
