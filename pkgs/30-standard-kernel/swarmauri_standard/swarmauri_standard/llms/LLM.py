import asyncio
import json
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Dict,
    FrozenSet,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
)

import httpx
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.messages.MessageBase import MessageBase

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.utils.duration_manager import DurationManager
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type()
class LLM(LLMBase):
    """
    Generic LLM class for interacting with various language model APIs. This
    class
    provides synchronous and asynchronous methods to send conversation data to
    the
    model, receive predictions, and stream responses.

    Attributes:
        api_key (SecretStr): API key for authenticating requests to the API.
        allowed_models (List[str]): List of allowed model names that can be
        used.
        name (str): The default model name to use for predictions.
        type (Literal["LLM"]): The type identifier for this class.
        BASE_URL (str): The base URL for API requests.
        timeout (float): Timeout for API requests in seconds.
    """

    capabilities: ClassVar[FrozenSet[str]] = frozenset(
        {
            "chat_completions",
            "structured_output",
            "multimodal_input",
            "streaming",
            "stream_usage",
        }
    )

    def __init__(self, **data) -> None:
        """
        Initialize the LLM class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
                   Should include api_key, and optionally name, BASE_URL,
                   timeout.
        """
        super().__init__(**data)

        self._headers = self._build_headers()

        # Load allowed models and set default if needed
        if not self.allowed_models:
            self.allowed_models = self.get_allowed_models()

        if not self.name and self.allowed_models:
            self.name = self.allowed_models[0]

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers, allowing provider subclasses to override."""
        headers = {"Content-Type": "application/json"}
        if self.api_key is not None:
            headers["Authorization"] = (
                f"Bearer {self.api_key.get_secret_value()}"
            )
        return headers

    def _build_endpoint(self) -> str:
        """Return the complete inference endpoint.

        ``BASE_URL`` remains a complete endpoint for backward compatibility.
        Provider subclasses may assemble an endpoint from provider fields.
        """
        if not self.BASE_URL:
            raise ValueError("BASE_URL must identify an inference endpoint")
        return self.BASE_URL

    def _build_payload(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
        top_p: float,
        enable_json: bool,
        stop: Optional[List[str]],
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Build an OpenAI-compatible chat-completions payload."""
        payload: Dict[str, Any] = {
            "model": self.name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = {"type": "json_object"}
        if stream:
            payload["stream"] = True
            if self.include_usage and "stream_usage" in self.capabilities:
                payload["stream_options"] = {"include_usage": True}
        return payload

    def _parse_response(
        self, response_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Parse content and usage from a chat-completions response."""
        content = response_data["choices"][0]["message"].get("content")
        return content or "", response_data.get("usage") or {}

    def _parse_stream_chunk(
        self, line: str
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Parse one server-sent chat-completions event."""
        if not line.startswith("data: "):
            return None, {}
        payload = line[6:].strip()
        if not payload or payload == "[DONE]":
            return None, {}
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            return None, {}
        usage = chunk.get("usage") or {}
        choices = chunk.get("choices") or []
        if not choices:
            return None, usage
        content = (choices[0].get("delta") or {}).get("content")
        return content, usage

    def _format_messages(
        self,
        messages: List[Type[MessageBase]],
    ) -> List[Dict[str, Any]]:
        """
        Formats conversation messages into the structure expected by the API.

        Args:
            messages (List[MessageBase]): List of message objects from the
            conversation history.

        Returns:
            List[Dict[str, Any]]: List of formatted message dictionaries.
        """
        formatted_messages = []
        for message in messages:
            formatted_message = message.model_dump(
                include=["content", "role", "name"], exclude_none=True
            )

            # Handle multi-modal content
            if isinstance(formatted_message["content"], list):
                formatted_message["content"] = [
                    {"type": item["type"], **item}
                    for item in formatted_message["content"]
                ]

            formatted_messages.append(formatted_message)
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data: Dict[str, Any],
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
    ) -> UsageData:
        """
        Prepare usage data by combining token counts and timing information.

        Args:
            usage_data: Raw usage data containing token counts.
            prompt_time (float): Time taken for prompt processing.
            completion_time (float): Time taken for response completion.

        Returns:
            UsageData: Processed usage data.
        """
        total_time = prompt_time + completion_time

        # Extract standard usage metrics
        usage = UsageData(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    @retry_on_status_codes()
    def predict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Generates a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message
            history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response
            termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = self._build_payload(
            formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop,
        )

        # Make the API request and measure time
        with DurationManager() as prompt_timer:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self._build_endpoint(),
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()

        # Parse the response
        response_data = response.json()
        message_content, usage_data = self._parse_response(response_data)

        # Prepare usage data if tracking is enabled
        if self.include_usage:
            usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
            conversation.add_message(
                AgentMessage(content=message_content, usage=usage)
            )
        else:
            conversation.add_message(AgentMessage(content=message_content))
        return conversation

    @retry_on_status_codes()
    async def apredict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Async method to generate a response from the model based on the given
        conversation.

        Args:
            conversation (Conversation): Conversation object with message
            history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response
            termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = self._build_payload(
            formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop,
        )

        # Make the async API request and measure time
        with DurationManager() as prompt_timer:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._build_endpoint(),
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()

        # Parse the response
        response_data = response.json()
        message_content, usage_data = self._parse_response(response_data)

        # Prepare usage data if tracking is enabled
        if self.include_usage:
            usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
            conversation.add_message(
                AgentMessage(content=message_content, usage=usage)
            )
        else:
            conversation.add_message(AgentMessage(content=message_content))

        return conversation

    @retry_on_status_codes()
    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Generator[str, None, None]:
        """
        Streams response text from the model in real-time.

        Args:
            conversation (Conversation): Conversation object with message
            history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response
            termination.

        Yields:
            str: Partial response content from the model.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = self._build_payload(
            formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop,
            stream=True,
        )

        # Start timing for prompt processing
        with DurationManager() as prompt_timer:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream(
                    "POST",
                    self._build_endpoint(),
                    headers=self._build_headers(),
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    message_content = ""
                    usage_data: Dict[str, Any] = {}
                    with DurationManager() as completion_timer:
                        for line in response.iter_lines():
                            content, chunk_usage = self._parse_stream_chunk(
                                line
                            )
                            if chunk_usage:
                                usage_data = chunk_usage
                            if content is not None:
                                message_content += content
                                yield content

        # Add the complete message to the conversation
        if self.include_usage:
            usage = self._prepare_usage_data(
                usage_data, prompt_timer.duration, completion_timer.duration
            )
            conversation.add_message(
                AgentMessage(content=message_content, usage=usage)
            )
        else:
            conversation.add_message(AgentMessage(content=message_content))

    @retry_on_status_codes()
    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that streams response text from the model in real-time.

        Args:
            conversation (Conversation): Conversation object with message
            history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response
            termination.

        Yields:
            str: Partial response content from the model.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = self._build_payload(
            formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            enable_json=enable_json,
            stop=stop,
            stream=True,
        )

        # Start timing for prompt processing
        with DurationManager() as prompt_timer:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    self._build_endpoint(),
                    headers=self._build_headers(),
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    message_content = ""
                    usage_data: Dict[str, Any] = {}
                    with DurationManager() as completion_timer:
                        async for line in response.aiter_lines():
                            content, chunk_usage = self._parse_stream_chunk(
                                line
                            )
                            if chunk_usage:
                                usage_data = chunk_usage
                            if content is not None:
                                message_content += content
                                yield content

        # Add the complete message to the conversation
        if self.include_usage:
            usage = self._prepare_usage_data(
                usage_data, prompt_timer.duration, completion_timer.duration
            )
            conversation.add_message(
                AgentMessage(content=message_content, usage=usage)
            )
        else:
            conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations and generates responses for each
        sequentially.

        Args:
            conversations (List[Conversation]): List of conversations to
            process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response
            termination.

        Returns:
            List[Conversation]: List of updated conversations with model
            responses.
        """
        results = []
        for conversation in conversations:
            result_conversation = self.predict(
                conversation,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                enable_json=enable_json,
                stop=stop,
            )
            results.append(result_conversation)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Async method for processing a batch of conversations concurrently.

        Args:
            conversations (List[Conversation]): List of conversations to
            process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response
            termination.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[Conversation]: List of updated conversations with model
            responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: Conversation) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    enable_json=enable_json,
                    stop=stop,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)

    def get_allowed_models(self) -> List[str]:
        """
        Returns a list of allowed models for this LLM provider.

        Provider-specific subclasses should override this to query their APIs.

        Returns:
            List[str]: List of allowed model names.
        """
        return self._get_models()

    def _get_models(self) -> List[str]:
        """Provider hook for model discovery without placeholder names."""
        return []
