import asyncio
import json
from pydantic import PrivateAttr
import httpx
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_standard.conversations.Conversation import Conversation
from typing import List, Optional, Dict, Literal, Any, AsyncGenerator, Generator

from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase

from swarmauri_standard.messages.AgentMessage import UsageData


class GroqModel(LLMBase):
    """
    GroqModel class for interacting with the Groq language models API. This class
    provides synchronous and asynchronous methods to send conversation data to the
    model, receive predictions, and stream responses.

    Attributes:
        api_key (str): API key for authenticating requests to the Groq API.
        allowed_models (List[str]): List of allowed model names that can be used.
        name (str): The default model name to use for predictions.
        type (Literal["GroqModel"]): The type identifier for this class.


    Allowed Models resources: https://console.groq.com/docs/models
    """

    api_key: str
    allowed_models: List[str] = [
        "gemma-7b-it",
        "gemma2-9b-it",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.2-11b-text-preview",
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-90b-text-preview",
        "llama-guard-3-8b",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "llama3-groq-70b-8192-tool-use-preview",
        "llama3-groq-8b-8192-tool-use-preview",
        "llava-v1.5-7b-4096-preview",
        "mixtral-8x7b-32768",
    ]
    name: str = "gemma-7b-it"
    type: Literal["GroqModel"] = "GroqModel"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(
        default="https://api.groq.com/openai/v1/chat/completions"
    )

    def __init__(self, **data):
        """
        Initialize the GroqAIAudio class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )
        self._async_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )

    def _format_messages(
        self,
        messages: List[SubclassUnion[MessageBase]],
    ) -> List[Dict[str, Any]]:
        """
        Formats conversation messages into the structure expected by the API.

        Args:
            messages (List[MessageBase]): List of message objects from the conversation history.

        Returns:
            List[Dict[str, Any]]: List of formatted message dictionaries.
        """

        formatted_messages = []
        for message in messages:
            formatted_message = message.model_dump(
                include=["content", "role", "name"], exclude_none=True
            )

            if isinstance(formatted_message["content"], list):
                formatted_message["content"] = [
                    {"type": item["type"], **item}
                    for item in formatted_message["content"]
                ]

            formatted_messages.append(formatted_message)
        return formatted_messages

    def _prepare_usage_data(self, usage_data) -> UsageData:
        """
        Prepares and validates usage data received from the API response.

        Args:
            usage_data (dict): Raw usage data from the API response.

        Returns:
            UsageData: Validated usage data instance.
        """
        return UsageData.model_validate(usage_data)

    @retry_on_status_codes((429, 529), max_retries=1)
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
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = self._client.post(self._BASE_URL, json=payload)

        response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
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
        Async method to generate a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
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
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Yields:
            str: Partial response content from the model.
        """

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = self._client.post(self._BASE_URL, json=payload)

        response.raise_for_status()

        message_content = ""
        for line in response.iter_lines():
            json_str = line.replace("data: ", "")
            try:
                if json_str:
                    chunk = json.loads(json_str)
                    if chunk["choices"][0]["delta"]:
                        delta = chunk["choices"][0]["delta"]["content"]
                        message_content += delta
                        yield delta
            except json.JSONDecodeError:
                pass

        conversation.add_message(AgentMessage(content=message_content))

    @retry_on_status_codes((429, 529), max_retries=1)
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
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Yields:
            str: Partial response content from the model.
        """

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = await self._async_client.post(self._BASE_URL, json=payload)

        response.raise_for_status()
        message_content = ""

        async for line in response.aiter_lines():
            json_str = line.replace("data: ", "")
            try:
                if json_str:
                    chunk = json.loads(json_str)
                    if chunk["choices"][0]["delta"]:
                        delta = chunk["choices"][0]["delta"]["content"]
                        message_content += delta
                        yield delta
            except json.JSONDecodeError:
                pass

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
        Processes a batch of conversations and generates responses for each sequentially.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
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
        max_concurrent=5,
    ) -> List[Conversation]:
        """
        Async method for processing a batch of conversations concurrently.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
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
