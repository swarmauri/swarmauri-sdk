import json
import time

from pydantic import Field
import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
from openai import OpenAI, AsyncOpenAI
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class OpenAIModel(LLMBase):
    """
    Provider resources: https://platform.openai.com/docs/models
    """

    api_key: str
    allowed_models: List[str] = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo",
        "gpt-4o-mini",
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-3.5-turbo-0125",
        # "chatgpt-4o-latest",
        # "gpt-3.5-turbo-instruct", # gpt-3.5-turbo-instruct does not support v1/chat/completions endpoint. only supports (/v1/completions)
        # "o1-preview",   # Does not support max_tokens and temperature
        # "o1-mini",      # Does not support max_tokens and temperature
        # "o1-preview-2024-09-12", # Does not support max_tokens and temperature
        # "o1-mini-2024-09-12",   # Does not support max_tokens and temperature
        # "gpt-4-0314",  #  it's deprecated
    ]
    name: str = "gpt-3.5-turbo"
    type: Literal["OpenAIModel"] = "OpenAIModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:

        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float,
        completion_time: float,
    ):
        """
        Prepares and extracts usage data and response timing.
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
            **filtered_usage_data
        )

        return usage

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = [],
    ):
        """Generates predictions using the OpenAI model."""
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(api_key=self.api_key)

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": stop,
        }

        if enable_json:
            kwargs["response_format"] = {"type": "json_object"}

        with DurationManager() as prompt_timer:
            response = client.chat.completions.create(**kwargs)

        with DurationManager() as completion_timer:
            result = json.loads(response.model_dump_json())
            message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
            completion_timer.duration,
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = [],
    ):
        """Asynchronous version of predict."""
        async_client = AsyncOpenAI(api_key=self.api_key)

        formatted_messages = self._format_messages(conversation.history)

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": stop,
        }

        if enable_json:
            kwargs["response_format"] = {"type": "json_object"}

        with DurationManager() as prompt_timer:
            response = await async_client.chat.completions.create(**kwargs)

        with DurationManager() as completion_timer:
            result = json.loads(response.model_dump_json())
            message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
            completion_timer.duration,
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    def stream(
        self, conversation, temperature=0.7, max_tokens=256, stop: List[str] = []
    ) -> Iterator[str]:
        """Synchronously stream the response token by token."""
        client = OpenAI(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            stream = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stop=stop,
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
        self, conversation, temperature=0.7, max_tokens=256, stop: List[str] = []
    ) -> AsyncIterator[str]:
        """Asynchronously stream the response token by token."""
        formatted_messages = self._format_messages(conversation.history)
        async_client = AsyncOpenAI(api_key=self.api_key)

        with DurationManager() as prompt_timer:
            stream = await async_client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stop=stop,
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
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = [],
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                enable_json=enable_json,
                stop=stop,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = [],
        max_concurrent=5,  # New parameter to control concurrency
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    enable_json=enable_json,
                    stop=stop,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
