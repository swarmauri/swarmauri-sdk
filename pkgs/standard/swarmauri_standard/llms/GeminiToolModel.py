import asyncio
import json
import logging
from typing import AsyncIterator, Iterator, List, Literal, Dict, Any
import httpx
from pydantic import PrivateAttr
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.GeminiSchemaConverter import (
    GeminiSchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri.utils.retry_decorator import retry_on_status_codes


class GeminiToolModel(LLMBase):
    """
    A class that interacts with Gemini-based LLM APIs to process conversations, handle tool calls, and
    convert messages for compatible schema. This model supports synchronous and asynchronous operations.

    Attributes:
        api_key (str): The API key used to authenticate requests to the Gemini API.
        allowed_models (List[str]): List of supported model names.
        name (str): The name of the Gemini model in use.
        type (Literal["GeminiToolModel"]): The model type, set to "GeminiToolModel".
    Providers Resources: https://ai.google.dev/api/python/google/generativeai/protos/

    """

    api_key: str
    allowed_models: List[str] = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        # "gemini-1.0-pro",  giving an unexpected response
    ]
    name: str = "gemini-1.5-pro"
    type: Literal["GeminiToolModel"] = "GeminiToolModel"
    _BASE_URL: str = PrivateAttr(
        default="https://generativelanguage.googleapis.com/v1beta/models"
    )
    _headers: Dict[str, str] = PrivateAttr(default={"Content-Type": "application/json"})

    _safety_settings: List[Dict[str, str]] = PrivateAttr(
        [
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

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        """
        Converts toolkit tools into a format compatible with the Gemini schema.

        Args:
            tools (dict): A dictionary of tools to convert.

        Returns:
            List[Dict[str, Any]]: List of converted tool definitions.
        """
        response = [GeminiSchemaConverter().convert(tools[tool]) for tool in tools]
        logging.info(response)
        return {"function_declarations": response}

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats message history for compatibility with Gemini API, sanitizing content and updating roles.

        Args:
            messages (List[SubclassUnion[MessageBase]]): A list of message objects.

        Returns:
            List[Dict[str, str]]: List of formatted message dictionaries.
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
                message["role"] = "user"

            # update content naming
            message["parts"] = {"text": message.pop("content")}

        return sanitized_messages

    def _process_tool_calls(self, tool_calls, toolkit, messages) -> List[MessageBase]:
        """
        Executes tool calls and appends results to the message list.

        Args:
            tool_calls (List[Dict]): List of tool calls to process.
            toolkit (Toolkit): Toolkit instance for handling tools.
            messages (List[MessageBase]): List of messages to update.

        Returns:
            List[MessageBase]: Updated list of messages.
        """
        tool_results = {}

        for tool_call in tool_calls:
            if "functionCall" in tool_call:
                func_name = tool_call["functionCall"]["name"]

                func_args = tool_call["functionCall"]["args"]
                logging.info(f"func_name: {func_name}")
                logging.info(f"func_args: {func_args}")

            func_call = toolkit.get_tool_by_name(func_name)
            func_result = func_call(**func_args)
            logging.info(f"func_result: {func_result}")
            tool_results[func_name] = func_result

        logging.info(f"messages: {messages}")

        messages.append(
            {
                "role": "function",
                "parts": [
                    {
                        "functionResponse": {
                            "name": fn,
                            "response": {
                                "result": val,  # Return the API response to Gemini
                            },
                        }
                    }
                    for fn, val in tool_results.items()
                ],
            }
        )
        return messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        """
        Extracts system context message from message history.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of message objects.

        Returns:
            str: Content of the system context message.
        """
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Conversation:
        """
        Generates model responses for a conversation synchronously.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit): Optional toolkit for handling tools.
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
        tools = self._schema_convert_tools(toolkit.tools)

        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
            "tools": [tools],
            "tool_config": tool_config,
        }

        system_context = self._get_system_context(conversation.history)

        if system_context:
            payload["system_instruction"] = system_context

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self._BASE_URL}/{self.name}:generateContent?key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        tool_response = response.json()

        formatted_messages.append(tool_response["candidates"][0]["content"])

        tool_calls = tool_response["candidates"][0]["content"]["parts"]

        messages = self._process_tool_calls(tool_calls, toolkit, formatted_messages)

        payload["contents"] = messages
        payload.pop("tools", None)
        payload.pop("tool_config", None)

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self._BASE_URL}/{self.name}:generateContent?key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        agent_response = response.json()
        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(
            AgentMessage(
                content=agent_response["candidates"][0]["content"]["parts"][0]["text"]
            )
        )

        logging.info(f"conversation: {conversation}")
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Conversation:
        """
        Asynchronously generates model responses for a conversation.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit): Optional toolkit for handling tools.
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
        tools = self._schema_convert_tools(toolkit.tools)

        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
            "tools": [tools],
            "tool_config": tool_config,
        }

        system_context = self._get_system_context(conversation.history)

        if system_context:
            payload["system_instruction"] = system_context

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._BASE_URL}/{self.name}:generateContent?key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        tool_response = response.json()

        formatted_messages.append(tool_response["candidates"][0]["content"])

        tool_calls = tool_response["candidates"][0]["content"]["parts"]

        messages = self._process_tool_calls(tool_calls, toolkit, formatted_messages)

        payload["contents"] = messages
        payload.pop("tools", None)
        payload.pop("tool_config", None)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._BASE_URL}/{self.name}:generateContent?key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        agent_response = response.json()
        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(
            AgentMessage(
                content=agent_response["candidates"][0]["content"]["parts"][0]["text"]
            )
        )

        logging.info(f"conversation: {conversation}")
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Iterator[str]:
        """
        Streams response generation in real-time.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit): Optional toolkit for handling tools.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Yields:
            str: Streamed text chunks from the model response.
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
        tools = self._schema_convert_tools(toolkit.tools)

        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
            "tools": [tools],
            "tool_config": tool_config,
        }

        system_context = self._get_system_context(conversation.history)

        if system_context:
            payload["system_instruction"] = system_context

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self._BASE_URL}/{self.name}:generateContent?key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        tool_response = response.json()

        formatted_messages.append(tool_response["candidates"][0]["content"])

        tool_calls = tool_response["candidates"][0]["content"]["parts"]

        messages = self._process_tool_calls(tool_calls, toolkit, formatted_messages)

        payload["contents"] = messages
        payload.pop("tools", None)
        payload.pop("tool_config", None)

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self._BASE_URL}/{self.name}:streamGenerateContent?alt=sse&key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            json_str = line.replace("data: ", "")
            if json_str:
                response_data = json.loads(json_str)
                chunk = response_data["candidates"][0]["content"]["parts"][0]["text"]
                full_response += chunk
                yield chunk

        conversation.add_message(AgentMessage(content=full_response))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response generation in real-time.

        Args:
            conversation (Conversation): The conversation instance.
            toolkit (Toolkit): Optional toolkit for handling tools.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Yields:
            str: Streamed text chunks from the model response.
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
        tools = self._schema_convert_tools(toolkit.tools)

        payload = {
            "contents": formatted_messages,
            "generation_config": generation_config,
            "safety_settings": self._safety_settings,
            "tools": [tools],
            "tool_config": tool_config,
        }

        system_context = self._get_system_context(conversation.history)

        if system_context:
            payload["system_instruction"] = system_context

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._BASE_URL}/{self.name}:generateContent?key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        tool_response = response.json()

        formatted_messages.append(tool_response["candidates"][0]["content"])

        tool_calls = tool_response["candidates"][0]["content"]["parts"]

        messages = self._process_tool_calls(tool_calls, toolkit, formatted_messages)

        payload["contents"] = messages
        payload.pop("tools", None)
        payload.pop("tool_config", None)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._BASE_URL}/{self.name}:streamGenerateContent?alt=sse&key={self.api_key}",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            json_str = line.replace("data: ", "")
            if json_str:
                response_data = json.loads(json_str)
                chunk = response_data["candidates"][0]["content"]["parts"][0]["text"]
                full_response += chunk
                yield chunk

        conversation.add_message(AgentMessage(content=full_response))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> List[Conversation]:
        """
        Processes multiple conversations synchronously.

        Args:
            conversations (List[Conversation]): List of conversation instances.
            toolkit (Toolkit): Optional toolkit for handling tools.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
        """
        return [
            self.predict(
                conv,
                toolkit=toolkit,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Asynchronously processes multiple conversations with concurrency control.

        Args:
            conversations (List[Conversation]): List of conversation instances.
            toolkit (Toolkit): Optional toolkit for handling tools.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit for generation.
            max_concurrent (int): Maximum number of concurrent asynchronous tasks.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
