import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase

<<<<<<< HEAD
from swarmauri_standard.conversations.Conversation import Conversation
=======
from swarmauri_core.conversations.IConversation import IConversation
>>>>>>> upstream/mono/dev
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.GeminiSchemaConverter import (
    GeminiSchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "GeminiToolModel")
class GeminiToolModel(ToolLLMBase):
    """
    A class that interacts with Gemini-based LLM APIs to process conversations, handle tool calls, and
    convert messages for compatible schema. This model supports synchronous and asynchronous operations.

    Attributes:
        api_key (SecretStr): The API key used to authenticate requests to the Gemini API.
        allowed_models (List[str]): List of supported model names.
        name (str): The name of the Gemini model in use.
        type (Literal["GeminiToolModel"]): The model type, set to "GeminiToolModel".
    Providers Resources: https://ai.google.dev/api/python/google/generativeai/protos/
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-pro-exp-02-05",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
    ]
    name: str = "gemini-1.5-pro"

    type: Literal["GeminiToolModel"] = "GeminiToolModel"
    timeout: float = 600.0
    BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"

    _headers: Dict[str, str] = PrivateAttr(default={"Content-Type": "application/json"})

    _safety_settings: List[Dict[str, str]] = PrivateAttr(
        default=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the GeminiToolModel instance with the provided data.

        Args:
            *args (Any): Variable length argument list.
            **kwargs (Any): Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(*args, **kwargs)
        self.allowed_models = self.allowed_models or self.get_allowed_models()
        if not self.name and self.allowed_models:
            self.name = self.allowed_models[0]

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Returns the schema converter class for Gemini API.

        Returns:
            Type[SchemaConverterBase]: The GeminiSchemaConverter class.
        """
        return GeminiSchemaConverter

    def _schema_convert_tools(
        self, tools: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Converts toolkit tools into a format compatible with the Gemini schema.

        Args:
            tools (Dict[str, Any]): A dictionary of tools to convert.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing converted tool definitions.
        """
        if not tools:
            return {"function_declarations": []}

        converter = self.get_schema_converter()()
        response = [converter.convert(tools[tool]) for tool in tools]
        return {"function_declarations": response}

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, Any]]:
        """
        Formats message history for compatibility with Gemini API, sanitizing content and updating roles.

        Args:
            messages (List[Type[MessageBase]]): A list of message objects.

        Returns:
            List[Dict[str, Any]]: List of formatted message dictionaries.
        """
        message_properties = ["content", "role", "tool_call_id", "tool_calls"]
        sanitized_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "system"
        ]

        for message in sanitized_messages:
            if message["role"] == "assistant":
                message["role"] = "model"

            if message["role"] == "tool":
                message["role"] = "function"

            if "content" in message:
                message["parts"] = [{"text": message.pop("content")}]

        return sanitized_messages

    def _process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        toolkit: Toolkit,
        messages: List[Dict[str, Any]],
    ) -> tuple[List[Dict[str, Any]], List[FunctionMessage]]:
        """
        Executes tool calls and creates appropriate response messages.

        Args:
            tool_calls (List[Dict[str, Any]]): List of tool calls to process.
            toolkit (Toolkit): Toolkit instance for handling tools.
            messages (List[Dict[str, Any]]): List of messages in the conversation.

        Returns:
            tuple[List[Dict[str, Any]], List[FunctionMessage]]: A tuple containing (updated messages, tool messages for the conversation)
        """
        if not toolkit or not tool_calls:
            return messages, []

        tool_results = {}
        tool_messages = []

        for tool_call in tool_calls:
            if "functionCall" in tool_call:
                try:
                    func_name = tool_call["functionCall"]["name"]
                    func_args = tool_call["functionCall"]["args"]

                    func_call = toolkit.get_tool_by_name(func_name)
                    if not func_call:
                        logging.warning(f"Tool {func_name} not found in toolkit")
                        continue

                    func_result = func_call(**func_args)
                    tool_results[func_name] = func_result

                    # Create a FunctionMessage for each tool call result
                    tool_messages.append(
                        FunctionMessage(name=func_name, content=json.dumps(func_result))
                    )
                except Exception as e:
                    logging.error(f"Error processing tool call: {str(e)}")
                    continue

        # Update messages for Gemini's format
        if tool_results:
            messages.append(
                {
                    "role": "function",
                    "parts": [
                        {
                            "functionResponse": {
                                "name": fn,
                                "response": {
                                    "result": val,
                                },
                            }
                        }
                        for fn, val in tool_results.items()
                    ],
                }
            )

        return messages, tool_messages

    def _get_system_context(self, messages: List[Type[MessageBase]]) -> str:
        """
        Extracts system context message from message history.

        Args:
            messages (List[Type[MessageBase]]): List of message objects.

        Returns:
            str: Content of the system context message, or None if not found.
        """
        for message in messages:
            if message.role == "system":
                return message.content
        return None

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Generates model responses for a conversation synchronously.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit, optional): Optional toolkit for handling tools.
            tool_choice (Dict[str, Any], optional): Tool selection strategy (not used in Gemini but included for API compatibility)
            multiturn (bool): Whether to follow up a tool call with another LLM request.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Returns:
            IConversation: Updated conversation with model response.
        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        tool_config = {
            "function_calling_config": {"mode": "ANY"},
        }

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
        }

        # Add tools if toolkit provided
        if toolkit:
            tools = self._schema_convert_tools(toolkit.tools)
            payload["tools"] = [tools]
            payload["tool_config"] = tool_config

        system_context = self._get_system_context(conversation.history)
        if system_context:
            payload["system_instruction"] = {"parts": [{"text": system_context}]}

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.BASE_URL}/{self.name}:generateContent?key={self.api_key.get_secret_value()}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            tool_response = response.json()

        # Check if there are tool calls
        has_tool_calls = False
        if "candidates" in tool_response and tool_response["candidates"]:
            content = tool_response["candidates"][0]["content"]
            formatted_messages.append(content)

            if "parts" in content:
                tool_calls = content["parts"]
                for part in tool_calls:
                    if "functionCall" in part:
                        has_tool_calls = True
                        break

        # Process tool calls if present
        if has_tool_calls and toolkit:
            messages, tool_messages = self._process_tool_calls(
                tool_calls, toolkit, formatted_messages
            )
            if tool_messages:
                conversation.add_messages(tool_messages)

            # For multiturn, follow up with another request if there were tool calls
            if multiturn:
                payload["contents"] = messages
                if "tools" in payload:
                    payload.pop("tools")
                if "tool_config" in payload:
                    payload.pop("tool_config")

                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        f"{self.BASE_URL}/{self.name}:generateContent?key={self.api_key.get_secret_value()}",
                        json=payload,
                        headers=self._headers,
                    )
                    response.raise_for_status()
                    agent_response = response.json()

                if "candidates" in agent_response and agent_response["candidates"]:
                    content = agent_response["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                    conversation.add_message(AgentMessage(content=content))
        else:
            # If no tool calls, just add the assistant's message
            if "candidates" in tool_response and tool_response["candidates"]:
                content = tool_response["candidates"][0]["content"]["parts"][0]["text"]
                conversation.add_message(AgentMessage(content=content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Conversation:
        """
        Asynchronously generates model responses for a conversation.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit, optional): Optional toolkit for handling tools.
            tool_choice (Dict[str, Any], optional): Tool selection strategy (not used in Gemini but included for API compatibility)
            multiturn (bool): Whether to follow up a tool call with another LLM request.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Returns:
            Conversation: Updated conversation with model response.
        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        tool_config = {
            "function_calling_config": {"mode": "ANY"},
        }

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
        }

        # Add tools if toolkit provided
        if toolkit:
            tools = self._schema_convert_tools(toolkit.tools)
            payload["tools"] = [tools]
            payload["tool_config"] = tool_config

        system_context = self._get_system_context(conversation.history)
        if system_context:
            payload["system_instruction"] = {"parts": [{"text": system_context}]}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.BASE_URL}/{self.name}:generateContent?key={self.api_key.get_secret_value()}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            tool_response = response.json()

        # Check if there are tool calls
        has_tool_calls = False
        if "candidates" in tool_response and tool_response["candidates"]:
            content = tool_response["candidates"][0]["content"]
            formatted_messages.append(content)

            if "parts" in content:
                tool_calls = content["parts"]
                for part in tool_calls:
                    if "functionCall" in part:
                        has_tool_calls = True
                        break

        # Process tool calls if present
        if has_tool_calls and toolkit:
            messages, tool_messages = self._process_tool_calls(
                tool_calls, toolkit, formatted_messages
            )
            if tool_messages:
                conversation.add_messages(tool_messages)

            # For multiturn, follow up with another request if there were tool calls
            if multiturn:
                payload["contents"] = messages
                if "tools" in payload:
                    payload.pop("tools")
                if "tool_config" in payload:
                    payload.pop("tool_config")

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/{self.name}:generateContent?key={self.api_key.get_secret_value()}",
                        json=payload,
                        headers=self._headers,
                    )
                    response.raise_for_status()
                    agent_response = response.json()

                if "candidates" in agent_response and agent_response["candidates"]:
                    content = agent_response["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                    conversation.add_message(AgentMessage(content=content))
        else:
            # If no tool calls, just add the assistant's message
            if "candidates" in tool_response and tool_response["candidates"]:
                content = tool_response["candidates"][0]["content"]["parts"][0]["text"]
                conversation.add_message(AgentMessage(content=content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """
        Streams response generation in real-time.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit, optional): Optional toolkit for handling tools.
            tool_choice (Dict[str, Any], optional): Tool selection strategy (not used in Gemini but included for API compatibility)
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Yields:
            Iterator[str]: Streamed text chunks from the model response.
        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        tool_config = {
            "function_calling_config": {"mode": "ANY"},
        }

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
        }

        # Add tools if toolkit provided
        if toolkit:
            tools = self._schema_convert_tools(toolkit.tools)
            payload["tools"] = [tools]
            payload["tool_config"] = tool_config

        system_context = self._get_system_context(conversation.history)
        if system_context:
            payload["system_instruction"] = {"parts": [{"text": system_context}]}

        # First, handle tool calls
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.BASE_URL}/{self.name}:generateContent?key={self.api_key.get_secret_value()}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            tool_response = response.json()

        # Check if there are tool calls
        has_tool_calls = False
        if "candidates" in tool_response and tool_response["candidates"]:
            content = tool_response["candidates"][0]["content"]
            formatted_messages.append(content)

            if "parts" in content:
                tool_calls = content["parts"]
                for part in tool_calls:
                    if "functionCall" in part:
                        has_tool_calls = True
                        break

        # Process tool calls if present
        if has_tool_calls and toolkit:
            messages, tool_messages = self._process_tool_calls(
                tool_calls, toolkit, formatted_messages
            )
            if tool_messages:
                conversation.add_messages(tool_messages)

            # Now stream with tool results included
            payload["contents"] = messages
            if "tools" in payload:
                payload.pop("tools")
            if "tool_config" in payload:
                payload.pop("tool_config")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.BASE_URL}/{self.name}:streamGenerateContent?alt=sse&key={self.api_key.get_secret_value()}",
                    json=payload,
                    headers=self._headers,
                )
                response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                line_str = line.decode("utf-8") if isinstance(line, bytes) else line
                if not line_str or line_str.startswith("data: [DONE]"):
                    continue

                json_str = line_str.replace("data: ", "")
                if json_str:
                    try:
                        response_data = json.loads(json_str)
                        if (
                            "candidates" in response_data
                            and response_data["candidates"]
                        ):
                            candidate = response_data["candidates"][0]
                            if (
                                "content" in candidate
                                and "parts" in candidate["content"]
                            ):
                                parts = candidate["content"]["parts"]
                                if parts and "text" in parts[0]:
                                    chunk = parts[0]["text"]
                                    full_response += chunk
                                    yield chunk
                    except json.JSONDecodeError:
                        pass

            conversation.add_message(AgentMessage(content=full_response))
        else:
            # If no tool calls, just stream the response directly
            if "candidates" in tool_response and tool_response["candidates"]:
                content = tool_response["candidates"][0]["content"]["parts"][0]["text"]
                conversation.add_message(AgentMessage(content=content))
                yield content

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response generation in real-time.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit, optional): Optional toolkit for handling tools.
            tool_choice (Dict[str, Any], optional): Tool selection strategy (not used in Gemini but included for API compatibility)
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Yields:
            AsyncIterator[str]: Asynchronously streamed text chunks from the model response.
        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        tool_config = {
            "function_calling_config": {"mode": "ANY"},
        }

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
        }

        # Add tools if toolkit provided
        if toolkit:
            tools = self._schema_convert_tools(toolkit.tools)
            payload["tools"] = [tools]
            payload["tool_config"] = tool_config

        system_context = self._get_system_context(conversation.history)
        if system_context:
            payload["system_instruction"] = {"parts": [{"text": system_context}]}

        # First, handle tool calls
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.BASE_URL}/{self.name}:generateContent?key={self.api_key.get_secret_value()}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            tool_response = response.json()

        # Check if there are tool calls
        has_tool_calls = False
        if "candidates" in tool_response and tool_response["candidates"]:
            content = tool_response["candidates"][0]["content"]
            formatted_messages.append(content)

            if "parts" in content:
                tool_calls = content["parts"]
                for part in tool_calls:
                    if "functionCall" in part:
                        has_tool_calls = True
                        break

        # Process tool calls if present
        if has_tool_calls and toolkit:
            messages, tool_messages = self._process_tool_calls(
                tool_calls, toolkit, formatted_messages
            )
            if tool_messages:
                conversation.add_messages(tool_messages)

            # Now stream with tool results included
            payload["contents"] = messages
            if "tools" in payload:
                payload.pop("tools")
            if "tool_config" in payload:
                payload.pop("tool_config")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}/{self.name}:streamGenerateContent?alt=sse&key={self.api_key.get_secret_value()}",
                    json=payload,
                    headers=self._headers,
                )
                response.raise_for_status()

            full_response = ""
            async for line in response.aiter_lines():
                if not line or line == "data: [DONE]":
                    continue

                json_str = line.replace("data: ", "")
                if json_str:
                    try:
                        response_data = json.loads(json_str)
                        if (
                            "candidates" in response_data
                            and response_data["candidates"]
                        ):
                            candidate = response_data["candidates"][0]
                            if (
                                "content" in candidate
                                and "parts" in candidate["content"]
                            ):
                                parts = candidate["content"]["parts"]
                                if parts and "text" in parts[0]:
                                    chunk = parts[0]["text"]
                                    full_response += chunk
                                    yield chunk
                    except json.JSONDecodeError:
                        pass

            conversation.add_message(AgentMessage(content=full_response))
        else:
            # If no tool calls, just stream the response directly
            if "candidates" in tool_response and tool_response["candidates"]:
                content = tool_response["candidates"][0]["content"]["parts"][0]["text"]
                conversation.add_message(AgentMessage(content=content))
                yield content

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> List[Conversation]:
        """
        Processes multiple conversations synchronously.

        Args:
            conversations (List[Conversation]): List of conversation instances.
            toolkit (Toolkit, optional): Optional toolkit for handling tools.
            tool_choice (Dict[str, Any], optional): Tool selection strategy (not used in Gemini but included for API compatibility)
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
        """
        results = []
        for conv in conversations:
            result = self.predict(
                conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            results.append(result)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Asynchronously processes multiple conversations with concurrency control.

        Args:
            conversations (List[Conversation]): List of conversation instances.
            toolkit (Toolkit, optional): Optional toolkit for handling tools.
            tool_choice (Dict[str, Any], optional): Tool selection strategy (not used in Gemini but included for API compatibility)
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.
            max_concurrent (int): Maximum number of concurrent asynchronous tasks.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: Conversation) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)

    def get_allowed_models(self) -> List[str]:
        """
        Returns the list of allowed models for Gemini API.

        Returns:
            List[str]: A list of allowed model names.
        """
        return ["gemini-1.5-pro", "gemini-1.5-flash"]
