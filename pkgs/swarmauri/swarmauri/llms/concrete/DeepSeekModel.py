import json
from typing import List, Dict, Literal, AsyncIterator, Iterator
import openai
from openai import AsyncOpenAI
import asyncio
from pydantic import Field
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class DeepSeekModel(LLMBase):
    """
    Provider resources: https://platform.deepseek.com/api-docs/quick_start/pricing
    """

    api_key: str
    allowed_models: List[str] = ["deepseek-chat"]
    name: str = "deepseek-chat"
    type: Literal["DeepSeekModel"] = "DeepSeekModel"
    client: openai.OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = openai.OpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties) for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ):
        formatted_messages = self._format_messages(conversation.history)

        response = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            top_p=top_p,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ):
        """Asynchronous version of predict"""
        formatted_messages = self._format_messages(conversation.history)

        response = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            top_p=top_p,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> Iterator[str]:
        """Synchronously stream the response token by token"""
        formatted_messages = self._format_messages(conversation.history)

        stream = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=True,
            top_p=top_p,
        )

        collected_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> AsyncIterator[str]:
        """Asynchronously stream the response token by token"""
        formatted_messages = self._format_messages(conversation.history)

        stream = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=True,
            top_p=top_p,
        )

        collected_content = []
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                top_p=top_p,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
        max_concurrent=5,
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop,
                    top_p=top_p,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
