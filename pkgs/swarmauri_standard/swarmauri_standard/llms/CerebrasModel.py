# File: swarmauri_standard/llms/CerebrasModel.py

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Generator, List, Literal, Optional, Type

import httpx
from pydantic import SecretStr, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.messages.MessageBase import MessageBase

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(LLMBase, "CerebrasModel")
class CerebrasModel(LLMBase):
    """
    CerebrasModel class for interacting with the Cerebras AI API.
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        "llama-4-scout-17b-16e-instruct",
        "llama3.1-8b",
        "llama-3.3-70b",
        "deepseek-r1-distill-llama-70b",
    ]
    name: str = "llama3.1-8b"
    type: Literal["CerebrasModel"] = "CerebrasModel"

    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.cerebras.ai/v1/chat/completions")
    timeout: float = 600.0

    def __init__(self, **data):
        """
        Initialize the CerebrasModel with the provided API key.
        """
        super().__init__(**data)
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key.get_secret_value()}"},
            base_url=self._BASE_URL,
            timeout=self.timeout,
        )
        self._async_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key.get_secret_value()}"},
            base_url=self._BASE_URL,
            timeout=self.timeout,
        )

    def _format_messages(
        self,
        messages: List[Type[MessageBase]],
    ) -> List[Dict[str, Any]]:
        """
        Formats conversation messages into the structure expected by the API.
        """
        formatted_messages = []
        for message in messages:
            fm = message.model_dump(
                include=["content", "role", "name"], exclude_none=True
            )
            if isinstance(fm["content"], list):
                fm["content"] = [
                    {"type": item["type"], **item} for item in fm["content"]
                ]
            formatted_messages.append(fm)
        return formatted_messages

    def _prepare_usage_data(self, usage: Dict[str, Any]) -> UsageData:
        """
        Prepares and validates usage data from the API response.
        """
        return UsageData.model_validate(usage)

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        temperature: float = 0.0,
        max_completion_tokens: int = -1,
        top_p: float = 1.0,
        seed: int = 0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Synchronous completion request to the Cerebras API.
        """
        payload = {
            "model": self.name,
            "messages": self._format_messages(conversation.history),
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
            "top_p": top_p,
            "seed": seed,
            "stream": False,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = self._client.post(self._BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        if self.include_usage and usage:
            u = self._prepare_usage_data(usage)
            conversation.add_message(AgentMessage(content=content, usage=u))
        else:
            conversation.add_message(AgentMessage(content=content))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature: float = 0.0,
        max_completion_tokens: int = -1,
        top_p: float = 1.0,
        seed: int = 0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Asynchronous completion request to the Cerebras API.
        """
        payload = {
            "model": self.name,
            "messages": self._format_messages(conversation.history),
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
            "top_p": top_p,
            "seed": seed,
            "stream": False,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        if self.include_usage and usage:
            u = self._prepare_usage_data(usage)
            conversation.add_message(AgentMessage(content=content, usage=u))
        else:
            conversation.add_message(AgentMessage(content=content))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.0,
        max_completion_tokens: int = -1,
        top_p: float = 1.0,
        seed: int = 0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Generator[str, None, None]:
        """
        Streams response text from the Cerebras API in real-time.
        """
        payload = {
            "model": self.name,
            "messages": self._format_messages(conversation.history),
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
            "top_p": top_p,
            "seed": seed,
            "stream": True,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = self._client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        message = ""
        for line in response.iter_lines():
            chunk_str = line.replace("data: ", "")
            if not chunk_str:
                continue
            try:
                chunk = json.loads(chunk_str)
                delta = chunk["choices"][0]["delta"].get("content")
                if delta:
                    message += delta
                    yield delta
            except json.JSONDecodeError:
                continue

        conversation.add_message(AgentMessage(content=message))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.0,
        max_completion_tokens: int = -1,
        top_p: float = 1.0,
        seed: int = 0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous streaming from the Cerebras API.
        """
        payload = {
            "model": self.name,
            "messages": self._format_messages(conversation.history),
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
            "top_p": top_p,
            "seed": seed,
            "stream": True,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        message = ""
        async for line in response.aiter_lines():
            chunk_str = line.replace("data: ", "")
            if not chunk_str:
                continue
            try:
                chunk = json.loads(chunk_str)
                delta = chunk["choices"][0]["delta"].get("content")
                if delta:
                    message += delta
                    yield delta
            except json.JSONDecodeError:
                continue

        conversation.add_message(AgentMessage(content=message))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.0,
        max_completion_tokens: int = -1,
        top_p: float = 1.0,
        seed: int = 0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations sequentially.
        """
        results: List[Conversation] = []
        for conv in conversations:
            res = self.predict(
                conv,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
                top_p=top_p,
                seed=seed,
                enable_json=enable_json,
                stop=stop,
            )
            results.append(res)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.0,
        max_completion_tokens: int = -1,
        top_p: float = 1.0,
        seed: int = 0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations concurrently.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conv(conv: Conversation) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_completion_tokens=max_completion_tokens,
                    top_p=top_p,
                    seed=seed,
                    enable_json=enable_json,
                    stop=stop,
                )

        tasks = [process_conv(conv) for conv in conversations]
        return await asyncio.gather(*tasks)

    def get_allowed_models(self) -> List[str]:
        """
        Retrieves the list of available models from the Cerebras API.
        """
        response = self._client.get("https://api.cerebras.ai/v1/models")
        response.raise_for_status()
        data = response.json()
        return [model["id"] for model in data.get("data", [])]
