import asyncio
import json
from typing import (
    Any,
    AsyncIterator,
    ClassVar,
    Dict,
    FrozenSet,
    Iterator,
    List,
    Optional,
    Type,
)

import httpx
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import (
    SchemaConverterBase,
)
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.conversations.IConversation import IConversation

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type()
class ToolLLM(ToolLLMBase):
    capabilities: ClassVar[FrozenSet[str]] = frozenset(
        {"chat_completions", "tools", "streaming"}
    )

    def __init__(self, **data: dict[str, Any]) -> None:
        """
        Initialize the OpenAIToolModel class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = self._build_headers()
        self.allowed_models = self.allowed_models or self.get_allowed_models()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers, allowing provider subclasses to override."""
        headers = {"Content-Type": "application/json"}
        if self.api_key is not None:
            headers["Authorization"] = (
                f"Bearer {self.api_key.get_secret_value()}"
            )
        return headers

    def _build_endpoint(self) -> str:
        """Return the complete inference endpoint."""
        if not self.BASE_URL:
            raise ValueError("BASE_URL must identify an inference endpoint")
        return self.BASE_URL

    def _build_payload(
        self,
        messages: List[Dict[str, Any]],
        *,
        toolkit: Optional[Toolkit],
        tool_choice: Optional[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Build an OpenAI-compatible tool-calling payload."""
        payload: Dict[str, Any] = {
            "model": self.name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if toolkit is not None:
            payload["tools"] = self._schema_convert_tools(toolkit.tools)
            payload["tool_choice"] = tool_choice or "auto"
        if stream:
            payload["stream"] = True
        return payload

    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return the first provider message from a completion response."""
        return response_data["choices"][0]["message"]

    def _parse_stream_chunk(self, line: str) -> Optional[str]:
        """Parse text from one server-sent completion event."""
        if not line.startswith("data: "):
            return None
        payload = line[6:].strip()
        if not payload or payload == "[DONE]":
            return None
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            return None
        choices = chunk.get("choices") or []
        if not choices:
            return None
        return (choices[0].get("delta") or {}).get("content")

    def get_schema_converter(self) -> Type["SchemaConverterBase"]:
        return OpenAISchemaConverter()

    def _schema_convert_tools(
        self, tools: Dict[str, SubclassUnion[ToolBase]]
    ) -> List[Dict[str, Any]]:
        converter = self.get_schema_converter()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = [
            "content",
            "role",
            "name",
            "tool_call_id",
            "tool_calls",
        ]
        return [
            m.model_dump(include=message_properties, exclude_none=True)
            for m in messages
        ]

    def _process_tool_calls(
        self,
        tool_calls: List[Any],
        toolkit: Toolkit,
        messages: List[Type[MessageBase]],
    ) -> List[Type[MessageBase]]:
        """
        Processes a list of tool calls and appends the results to the messages
        list.

        Args:
            tool_calls (list): A list of dictionaries representing tool calls.
            Each dictionary should contain
                               a "function" key with a nested dictionary that
                               includes the "name" and "arguments"
                               of the function to be called, and an "id" key
                               for the tool call identifier.
            toolkit (Toolkit): An object that provides access to tools via the
            `get_tool_by_name` method.
            messages (list): A list of message dictionaries to which the
            results of the tool calls will be appended.

        Returns:
            List[MessageBase]: The updated list of messages with the results of
            the tool calls appended.
        """
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        return messages

    @staticmethod
    def _get_function_messages(
        messages: List[Dict[str, Any]],
    ) -> List[FunctionMessage]:
        """Create conversation messages from provider tool results."""
        return [
            FunctionMessage(
                tool_call_id=message["tool_call_id"],
                name=message["name"],
                content=message["content"],
            )
            for message in messages
            if message["role"] == "tool"
        ]

    @retry_on_status_codes()
    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Makes a synchronous prediction using the Groq model.

        Parameters:
            conversation (Conversation): Conversation instance with message
            history.
            toolkit (Tookit): Optional toolkit for tool conversion.
            tool_choice (dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            IConversation: Updated conversation with agent responses and tool
            calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._build_payload(
            formatted_messages,
            toolkit=toolkit,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self._build_endpoint(),
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()
            tool_response = response.json()

        provider_message = self._parse_response(tool_response)
        messages = [
            formatted_messages[-1],
            provider_message,
        ]
        tool_calls = provider_message.get("tool_calls", [])
        if tool_calls:
            conversation.add_message(
                AgentMessage(
                    content=provider_message.get("content"),
                    tool_calls=tool_calls,
                )
            )
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Add tool messages to Conversation to enable Conversation hooks
        conversation.add_messages(self._get_function_messages(messages))

        if multiturn:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self._build_endpoint(),
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()

            agent_response = self._parse_response(response.json())

            agent_message = AgentMessage(content=agent_response.get("content"))
            conversation.add_message(agent_message)
        return conversation

    @retry_on_status_codes()
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Makes an asynchronous prediction using the OpenAI model.

        Parameters:
            conversation (Conversation): Conversation instance with message
            history.
            toolkit (Tookit): Optional toolkit for tool conversion.
            tool_choice (dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            Conversation: Updated conversation with agent responses and tool
            calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._build_payload(
            formatted_messages,
            toolkit=toolkit,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_endpoint(),
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()
            tool_response = response.json()

        provider_message = self._parse_response(tool_response)
        messages = [
            formatted_messages[-1],
            provider_message,
        ]
        tool_calls = provider_message.get("tool_calls", [])
        if tool_calls:
            conversation.add_message(
                AgentMessage(
                    content=provider_message.get("content"),
                    tool_calls=tool_calls,
                )
            )
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Add tool messages to Conversation to enable Conversation hooks
        conversation.add_messages(self._get_function_messages(messages))

        if multiturn:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._build_endpoint(),
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()

            agent_response = self._parse_response(response.json())

            agent_message = AgentMessage(content=agent_response.get("content"))
            conversation.add_message(agent_message)
        return conversation

    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """
        Streams response from OpenAI model in real-time.

        Parameters:
            conversation (Conversation): Conversation instance with message
            history.
            toolkit (Tookit): Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            Iterator[str]: Streamed response content.
        """

        formatted_messages = self._format_messages(conversation.history)

        payload = self._build_payload(
            formatted_messages,
            toolkit=toolkit,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self._build_endpoint(),
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()

        tool_response = response.json()

        provider_message = self._parse_response(tool_response)
        messages = [formatted_messages[-1], provider_message]
        tool_calls = provider_message.get("tool_calls", [])

        if tool_calls:
            conversation.add_message(
                AgentMessage(
                    content=provider_message.get("content"),
                    tool_calls=tool_calls,
                )
            )

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        conversation.add_messages(self._get_function_messages(messages))

        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        message_content = ""
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream(
                "POST",
                self._build_endpoint(),
                headers=self._build_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    delta = self._parse_stream_chunk(line)
                    if delta is not None:
                        message_content += delta
                        yield delta

        conversation.add_message(AgentMessage(content=message_content))

    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response from Groq model.

        Parameters:
            conversation (Conversation): Conversation instance with message
            history.
            toolkit (Tookit): Optional toolkit for tool conversion.
            tool_choice (dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            AsyncIterator[str]: Streamed response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = self._build_payload(
            formatted_messages,
            toolkit=toolkit,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_endpoint(),
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()

        tool_response = response.json()

        provider_message = self._parse_response(tool_response)
        messages = [formatted_messages[-1], provider_message]
        tool_calls = provider_message.get("tool_calls", [])

        if tool_calls:
            conversation.add_message(
                AgentMessage(
                    content=provider_message.get("content"),
                    tool_calls=tool_calls,
                )
            )

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        conversation.add_messages(self._get_function_messages(messages))

        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        message_content = ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self._build_endpoint(),
                headers=self._build_headers(),
                json=payload,
            ) as agent_response:
                agent_response.raise_for_status()
                async for line in agent_response.aiter_lines():
                    delta = self._parse_stream_chunk(line)
                    if delta is not None:
                        message_content += delta
                        yield delta
        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations and generates responses for each
        sequentially.

        Args:
            conversations (List[Conversation]): List of conversations to
            process.
            temperature (float): Sampling temperature for response diversity.
            tool_choice dict[str, Any]): Tool selection strategy.
            toolkit (Tookit): Optional toolkit for tool conversion.
            max_tokens (int): Maximum tokens for each response.

        Returns:
            List[IConversation]: List of updated conversations with model
            responses.
        """
        return [
            self.predict(
                conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Async method for processing a batch of conversations concurrently.

        Args:
            conversations (List[Conversation]): List of conversations to
            process.
            temperature (float): Sampling temperature for response diversity.
            tool_choice (dict[str, Any]): Tool selection strategy.
            toolkit (Tookit): Optional toolkit for tool conversion.s
            max_tokens (int): Maximum tokens for each response.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[Conversation]: List of updated conversations with model
            responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
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
        Get the list of allowed models for the OpenAI API.

        Returns:
            List[str]: List of allowed models.
        """
        return self._get_models()

    def _get_models(self) -> List[str]:
        """Provider hook for model discovery without placeholder names."""
        return []
