import json
import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
from pydantic import Field
import cohere
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class CohereModel(LLMBase):
    """
    Provider resources: https://docs.cohere.com/docs/models#command

    """

    api_key: str
    allowed_models: List[str] = [
        "command-r-plus-08-2024",
        "command-r-plus-04-2024",
        "command-r-03-2024",
        "command-r-08-2024",
        "command-light",
        "command",
    ]
    name: str = "command"
    type: Literal["CohereModel"] = "CohereModel"
    client: cohere.ClientV2 = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = cohere.ClientV2(api_key=self.api_key)

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        formatted_messages = []
        for message in messages:
            role = message.role
            if role == "assistant":
                role = "assistant"
            formatted_messages.append({"role": role, "content": message.content})
        return formatted_messages

    def predict(self, conversation, temperature=0.7, max_tokens=256):
        formatted_messages = self._format_messages(conversation.history)

        response = self.client.chat(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        message_content = response.message.content[0].text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

    async def apredict(self, conversation, temperature=0.7, max_tokens=256):
        formatted_messages = self._format_messages(conversation.history)

        response = await asyncio.to_thread(
            self.client.chat,
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        message_content = response.message.content[0].text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

    def stream(self, conversation, temperature=0.7, max_tokens=256) -> Iterator[str]:
        formatted_messages = self._format_messages(conversation.history)

        stream = self.client.chat_stream(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        collected_content = []
        for chunk in stream:
            if chunk and chunk.type == "content-delta":
                content = chunk.delta.message.content.text
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def astream(
        self, conversation, temperature=0.7, max_tokens=256
    ) -> AsyncIterator[str]:
        formatted_messages = self._format_messages(conversation.history)

        stream = await asyncio.to_thread(
            self.client.chat_stream,
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        collected_content = []
        for chunk in stream:
            if chunk and chunk.type == "content-delta":
                content = chunk.delta.message.content.text
                collected_content.append(content)
                yield content
            await asyncio.sleep(0)  # Allow other tasks to run

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    def batch(self, conversations: List, temperature=0.7, max_tokens=256) -> List:
        return [
            self.predict(conv, temperature=temperature, max_tokens=max_tokens)
            for conv in conversations
        ]

    async def abatch(
        self, conversations: List, temperature=0.7, max_tokens=256, max_concurrent=5
    ) -> List:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv, temperature=temperature, max_tokens=max_tokens
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
