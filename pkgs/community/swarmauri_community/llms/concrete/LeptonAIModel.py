import json
from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Literal, Optional, Iterator, AsyncIterator
import asyncio
from pydantic import Field
from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class LeptonAIModel(LLMBase):
    """
    Provider resources: https://www.lepton.ai/playground
    """

    api_key: str
    allowed_models: List[str] = [
        "llama2-13b",
        "llama3-1-405b",
        "llama3-1-70b",
        "llama3-1-8b",
        "llama3-70b",
        "llama3-8b",
        "mixtral-8x7b",
        "mistral-7b",
        "nous-hermes-llama2-13b",
        "openchat-3-5",
        "qwen2-72b",
        "toppy-m-7b",
        "wizardlm-2-7b",
        "wizardlm-2-8x22b",
    ]

    name: str = "llama3-8b"
    type: Literal["LeptonAIModel"] = "LeptonAIModel"
    client: OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        url = f"https://{self.name}.lepton.run/api/v1/"
        self.client = OpenAI(base_url=url, api_key=self.api_key)
        self.async_client = AsyncOpenAI(base_url=url, api_key=self.api_key)

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

    def _prepare_messages(self, conversation):
        formatted_messages = self._format_messages(conversation.history)
        system_context = self._get_system_context(conversation.history)
        if system_context:
            formatted_messages = [
                {"role": "system", "content": system_context},
                formatted_messages[-1],
            ]
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
    ):
        """
        Prepares and extracts usage data and response timing.
        """
        total_time = prompt_time + completion_time

        usage = UsageData(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    def predict(
        self,
        conversation,
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
        stream: Optional[bool] = False,
    ):
        formatted_messages = self._prepare_messages(conversation)

        with DurationManager() as prompt_timer:
            response = self.client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=stream,
            )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    async def apredict(
        self,
        conversation,
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
    ):
        """Asynchronous version of predict"""
        formatted_messages = self._prepare_messages(conversation)

        with DurationManager() as prompt_timer:
            response = await self.async_client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    def stream(
        self,
        conversation,
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
    ) -> Iterator[str]:
        """Synchronously stream the response token by token"""
        formatted_messages = self._prepare_messages(conversation)

        with DurationManager() as prompt_timer:
            stream = self.client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True,
                stream_options={"include_usage": True},
            )

        collected_content = []
        usage_data = {}

        with DurationManager() as completion_timer:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    yield content

                if hasattr(chunk, "usage") and chunk.usage is not None:
                    usage_data = chunk.usage

        full_content = "".join(collected_content)
        usage = self._prepare_usage_data(
            usage_data.model_dump(),
            prompt_timer.duration,
            completion_timer.duration,
        )

        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    async def astream(
        self,
        conversation,
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
    ) -> AsyncIterator[str]:
        """Asynchronously stream the response token by token"""
        formatted_messages = self._prepare_messages(conversation)

        with DurationManager() as prompt_timer:
            stream = await self.async_client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True,
                stream_options={"include_usage": True},
            )

        usage_data = {}
        collected_content = []

        with DurationManager() as completion_timer:
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    yield content

                if hasattr(chunk, "usage") and chunk.usage is not None:
                    usage_data = chunk.usage

        full_content = "".join(collected_content)

        usage = self._prepare_usage_data(
            usage_data.model_dump(),
            prompt_timer.duration,
            completion_timer.duration,
        )
        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    def batch(
        self,
        conversations: List,
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature: Optional[float] = 0.5,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 0.8,
        max_concurrent: int = 5,
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
