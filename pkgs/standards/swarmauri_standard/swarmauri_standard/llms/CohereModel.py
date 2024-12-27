import json
import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
from pydantic import PrivateAttr
import httpx

from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_standard.messages.AgentMessage import UsageData
from swarmauri.utils.duration_manager import DurationManager


class CohereModel(LLMBase):
    """
    This class provides both synchronous and asynchronous methods for interacting with
    Cohere's chat endpoints, supporting single messages, streaming, and batch processing.

    Attributes:
        api_key (str): The authentication key for accessing Cohere's API.
        allowed_models (List[str]): List of supported Cohere model identifiers.
        name (str): The default model name to use (defaults to "command").
        type (Literal["CohereModel"]): The type identifier for this model class.

    Link to Allowed Models: https://docs.cohere.com/docs/models
    Link to API Key: https://dashboard.cohere.com/api-keys
    """

    _BASE_URL: str = PrivateAttr("https://api.cohere.ai/v1")
    _client: httpx.Client = PrivateAttr()

    api_key: str
    allowed_models: List[str] = [
        "command",
        "command-r-plus-08-2024",
        "command-r-plus-04-2024",
        "command-r-03-2024",
        "command-r-08-2024",
        "command-light",
    ]
    name: str = "command"
    type: Literal["CohereModel"] = "CohereModel"

    def __init__(self, **data):
        """
        Initialize the CohereModel with the provided configuration.

        Args:
            **data: Keyword arguments for model configuration, must include 'api_key'.
        """
        super().__init__(**data)
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }
        self._client = httpx.Client(
            headers=headers, base_url=self._BASE_URL, timeout=30
        )

    def get_headers(self) -> Dict[str, str]:
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

    def _format_messages(
        self, messages: List[MessageBase]
    ) -> tuple[List[Dict[str, str]], str, str]:
        """
        Format a list of messages into Cohere's expected chat format.

        Args:
            messages: List of MessageBase objects containing the conversation history.

        Returns:
            tuple containing:
                - List[Dict[str, str]]: Formatted chat history
                - str: System message (if any)
                - str: Latest user message
        """
        chat_history = []
        system_message = None
        user_message = None

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            elif msg.role == "human":
                user_message = msg.content
            elif msg.role == "assistant" and len(chat_history) > 0:
                last_entry = chat_history[-1]
                last_entry["text"] = msg.content
            elif msg.role == "human" and user_message != msg.content:
                chat_history.append(
                    {
                        "user_name": "Human",
                        "message": msg.content,
                        "text": "",
                    }
                )

        chat_history = [h for h in chat_history if h["text"]]

        return chat_history, system_message, user_message

    def _prepare_usage_data(
        self,
        usage_data: Dict,
        prompt_time: float,
        completion_time: float,
    ) -> UsageData:
        """
        Prepare usage statistics from API response and timing data.

        Args:
            usage_data: Dictionary containing token usage information from the API
            prompt_time: Time taken to send the prompt
            completion_time: Time taken to receive the completion

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

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(self, conversation, temperature=0.7, max_tokens=256):
        """
        Generate a single prediction from the model synchronously.

        Args:
            conversation: The conversation object containing message history
            temperature (float, optional): Sampling temperature. Defaults to 0.7
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256

        Returns:
            The updated conversation object with the model's response added

        Raises:
            httpx.HTTPError: If the API request fails
        """
        chat_history, system_message, message = self._format_messages(
            conversation.history
        )

        if not message:
            if conversation.history:
                message = conversation.history[-1].content
            else:
                message = ""

        payload = {
            "message": message,
            "chat_history": chat_history,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            payload["preamble"] = system_message

        with DurationManager() as prompt_timer:
            response = self._client.post("/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        with DurationManager() as completion_timer:
            message_content = data["text"]

        usage_data = data.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(self, conversation, temperature=0.7, max_tokens=256):
        """
        Generate a single prediction from the model asynchronously.

        Args:
            conversation: The conversation object containing message history
            temperature (float, optional): Sampling temperature. Defaults to 0.7
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256

        Returns:
            The updated conversation object with the model's response added

        Raises:
            httpx.HTTPError: If the API request fails
        """
        chat_history, system_message, message = self._format_messages(
            conversation.history
        )

        if not message:
            if conversation.history:
                message = conversation.history[-1].content
            else:
                message = ""

        payload = {
            "message": message,
            "chat_history": chat_history,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            payload["preamble"] = system_message

        async with httpx.AsyncClient(
            headers=self.get_headers(), base_url=self._BASE_URL
        ) as client:
            with DurationManager() as prompt_timer:
                response = await client.post("/chat", json=payload)
                response.raise_for_status()
                data = response.json()

            with DurationManager() as completion_timer:
                message_content = data["text"]

            usage_data = data.get("usage", {})

            usage = self._prepare_usage_data(
                usage_data, prompt_timer.duration, completion_timer.duration
            )

            conversation.add_message(AgentMessage(content=message_content, usage=usage))
            return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(self, conversation, temperature=0.7, max_tokens=256) -> Iterator[str]:
        """
        Stream responses from the model synchronously, yielding content as it becomes available.

        This method processes the conversation and streams the model's response piece by piece,
        allowing for real-time processing of the output. At the end of streaming, it adds the
        complete response to the conversation history.

        Args:
            conversation: The conversation object containing message history
            temperature (float, optional): Sampling temperature. Controls randomness in the response.
                Higher values (e.g., 0.8) create more diverse outputs, while lower values (e.g., 0.2)
                make outputs more deterministic. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate in the response.
                Defaults to 256.

        Yields:
            str: Chunks of the model's response as they become available.

        Returns:
            None: The method updates the conversation object in place after completion.
        """
        chat_history, system_message, message = self._format_messages(
            conversation.history
        )

        if not message and conversation.history:
            message = conversation.history[-1].content

        payload = {
            "message": message or "",
            "chat_history": chat_history,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if system_message:
            payload["preamble"] = system_message

        collected_content = []
        usage_data = {}

        with DurationManager() as prompt_timer:
            response = self._client.post("/chat", json=payload)
            response.raise_for_status()

        with DurationManager() as completion_timer:
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

        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self, conversation, temperature=0.7, max_tokens=256
    ) -> AsyncIterator[str]:
        """
        Stream responses from the model asynchronously, yielding content as it becomes available.

        This method is the asynchronous version of `stream()`. It processes the conversation and
        streams the model's response piece by piece using async/await syntax. The method creates
        and manages its own AsyncClient instance to prevent event loop issues.

        Args:
            conversation: The conversation object containing message history
            temperature (float, optional): Sampling temperature. Controls randomness in the response.
                Higher values (e.g., 0.8) create more diverse outputs, while lower values (e.g., 0.2)
                make outputs more deterministic. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate in the response.
                Defaults to 256.

        Yields:
            str: Chunks of the model's response as they become available.

        Returns:
            None: The method updates the conversation object in place after completion.
        """

        chat_history, system_message, message = self._format_messages(
            conversation.history
        )

        if not message:
            if conversation.history:
                message = conversation.history[-1].content
            else:
                message = ""

        payload = {
            "message": message,
            "chat_history": chat_history,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if system_message:
            payload["preamble"] = system_message

        collected_content = []
        usage_data = {}

        async with httpx.AsyncClient(
            headers=self.get_headers(), base_url=self._BASE_URL
        ) as client:
            with DurationManager() as prompt_timer:
                response = await client.post("/chat", json=payload)
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

            conversation.add_message(AgentMessage(content=full_content, usage=usage))

    def batch(self, conversations: List, temperature=0.7, max_tokens=256) -> List:
        """
        Process multiple conversations synchronously.

        Args:
            conversations: List of conversation objects to process
            temperature (float, optional): Sampling temperature. Defaults to 0.7
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256

        Returns:
            List of updated conversation objects with model responses added
        """
        return [
            self.predict(conv, temperature=temperature, max_tokens=max_tokens)
            for conv in conversations
        ]

    async def abatch(
        self, conversations: List, temperature=0.7, max_tokens=256, max_concurrent=5
    ) -> List:
        """
        Process multiple conversations asynchronously with concurrency control.

        Args:
            conversations: List of conversation objects to process
            temperature (float, optional): Sampling temperature. Defaults to 0.7
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256
            max_concurrent (int, optional): Maximum number of concurrent requests. Defaults to 5

        Returns:
            List of updated conversation objects with model responses added
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv, temperature=temperature, max_tokens=max_tokens
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
