from pydantic import Field
import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
import ai21
from ai21 import AsyncAI21Client
from ai21.models.chat import ChatMessage
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class AI21StudioModel(LLMBase):
    """
    Provider resources: https://docs.ai21.com/reference/jamba-15-api-ref
    """

    api_key: str
    allowed_models: List[str] = [
        "jamba-1.5-large",
        "jamba-1.5-mini",
    ]
    name: str = "jamba-1.5-mini"
    type: Literal["AI21StudioModel"] = "AI21StudioModel"
    client: ai21.AI21Client = Field(default=None, exclude=True)
    async_client: AsyncAI21Client = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.client = ai21.AI21Client(api_key=self.api_key)
        self.async_client = AsyncAI21Client(api_key=self.api_key)

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[ChatMessage]:
        return [
            ChatMessage(content=message.content, role=message.role)
            for message in messages
        ]

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
    ):
        formatted_messages = self._format_messages(conversation.history)

        response = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            n=n,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
    ):
        formatted_messages = self._format_messages(conversation.history)

        response = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            n=n,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
    ) -> Iterator[str]:
        formatted_messages = self._format_messages(conversation.history)

        stream = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            stream=True,
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
        top_p=1.0,
        stop="\n",
    ) -> AsyncIterator[str]:
        formatted_messages = self._format_messages(conversation.history)

        stream = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            stream=True,
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
        top_p=1.0,
        stop="\n",
        n=1,
    ) -> List:
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                n=n,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
        max_concurrent=5,
    ) -> List:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stop=stop,
                    n=n,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
