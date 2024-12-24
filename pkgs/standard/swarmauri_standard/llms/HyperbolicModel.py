import asyncio
import json
from pydantic import PrivateAttr
import httpx
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri.utils.duration_manager import DurationManager
from swarmauri_standard.conversations.Conversation import Conversation
from typing import List, Optional, Dict, Literal, Any, AsyncGenerator, Generator

from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase

from swarmauri_standard.messages.AgentMessage import UsageData


class HyperbolicModel(LLMBase):
    """
    HyperbolicModel class for interacting with the Hyperbolic AI language models API.

    Attributes:
        api_key (str): API key for authenticating requests to the Hyperbolic API.
        allowed_models (List[str]): List of allowed model names that can be used.
        name (str): The default model name to use for predictions.
        type (Literal["HyperbolicModel"]): The type identifier for this class.

    Link to Allowed Models: https://app.hyperbolic.xyz/models
    Link to API KEYS: https://app.hyperbolic.xyz/settings
    """

    api_key: str
    allowed_models: List[str] = [
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        "meta-llama/Llama-3.2-3B-Instruct",
        "Qwen/Qwen2.5-72B-Instruct",
        "deepseek-ai/DeepSeek-V2.5",
        "meta-llama/Meta-Llama-3-70B-Instruct",
        "NousResearch/Hermes-3-Llama-3.1-70B",
        "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
    ]
    name: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    type: Literal["HyperbolicModel"] = "HyperbolicModel"
    _BASE_URL: str = PrivateAttr(
        default="https://api.hyperbolic.xyz/v1/chat/completions"
    )
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data) -> None:
        """
        Initialize the HyperbolicModel class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

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

    def _prepare_usage_data(
        self,
        usage_data,
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

        # Filter usage data for relevant keys
        filtered_usage_data = {
            key: value
            for key, value in usage_data.items()
            if key
            not in {
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "prompt_time",
                "completion_time",
                "total_time",
            }
        }

        usage = UsageData(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
            **filtered_usage_data,
        )

        return usage

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = -1,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Generates a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (Optional[int]): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            top_k (int): Maximum number of tokens to consider at each step.
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
            "top_p": top_p,
            "top_k": top_k,
            "stream": False,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stop is not None:
            payload["stop"] = stop

        with DurationManager() as promt_timer:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        response_data = response.json()
        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data, promt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = -1,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Async method to generate a response from the model based on the given conversation.

        Args are same as predict method.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": False,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stop is not None:
            payload["stop"] = stop

        with DurationManager() as promt_timer:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        response_data = response.json()
        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data, promt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = -1,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Generator[str, None, None]:
        """
        Streams response text from the model in real-time.

        Args are same as predict method.

        Yields:
            str: Partial response content from the model.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": True,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stop is not None:
            payload["stop"] = stop

        with DurationManager() as promt_timer:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        message_content = ""
        usage_data = {}
        with DurationManager() as completion_timer:
            for line in response.iter_lines():
                json_str = line.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if chunk["choices"] and chunk["choices"][0]["delta"]:
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                        if "usage" in chunk and chunk["usage"] is not None:
                            usage_data = chunk["usage"]
                except json.JSONDecodeError:
                    pass

        usage = self._prepare_usage_data(
            usage_data, promt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = -1,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that streams response text from the model in real-time.

        Args are same as predict method.

        Yields:
            str: Partial response content from the model.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": True,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stop is not None:
            payload["stop"] = stop

        with DurationManager() as promt_timer:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        message_content = ""
        usage_data = {}
        with DurationManager() as completion_timer:
            async for line in response.aiter_lines():
                json_str = line.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if chunk["choices"] and chunk["choices"][0]["delta"]:
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                        if "usage" in chunk and chunk["usage"] is not None:
                            usage_data = chunk["usage"]
                except json.JSONDecodeError:
                    pass

        usage = self._prepare_usage_data(
            usage_data, promt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = -1,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations and generates responses for each sequentially.

        Args are same as predict method.
        """
        results = []
        for conversation in conversations:
            result_conversation = self.predict(
                conversation,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                enable_json=enable_json,
                stop=stop,
            )
            results.append(result_conversation)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = -1,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
        max_concurrent=5,
    ) -> List[Conversation]:
        """
        Async method for processing a batch of conversations concurrently.

        Args are same as predict method, with additional arg:
            max_concurrent (int): Maximum number of concurrent requests.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: Conversation) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    enable_json=enable_json,
                    stop=stop,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
