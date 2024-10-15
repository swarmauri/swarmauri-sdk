import asyncio
import json
from typing import List, Literal, Dict
import mistralai
from anyio import sleep
from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class MistralModel(LLMBase):
    """Provider resources: https://docs.mistral.ai/getting-started/models/"""

    api_key: str
    allowed_models: List[str] = [
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest",
        "open-mistral-nemo",
        "codestral-latest",
        "open-codestral-mamba",
    ]
    name: str = "open-mixtral-8x7b"
    type: Literal["MistralModel"] = "MistralModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ):
        formatted_messages = self._format_messages(conversation.history)
        client = mistralai.Mistral(api_key=self.api_key)

        if enable_json:
            response = client.chat.complete(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )
        else:
            response = client.chat.complete(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )

        result = json.loads(response.json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def apredict(
        self,
        conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ):
        formatted_messages = self._format_messages(conversation.history)
        client = mistralai.Mistral(api_key=self.api_key)

        if enable_json:
            response = await client.chat.complete_async(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )
        else:
            response = await client.chat.complete_async(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )

        result = json.loads(response.json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def stream(
        self,
        conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        safe_prompt: bool = False,
    ):
        formatted_messages = self._format_messages(conversation.history)
        client = mistralai.Mistral(api_key=self.api_key)

        stream_response = client.chat.stream(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safe_prompt=safe_prompt,
        )
        message_content = ""

        for chunk in stream_response:
            if chunk.data.choices[0].delta.content:
                message_content += chunk.data.choices[0].delta.content
                yield chunk.data.choices[0].delta.content

        conversation.add_message(AgentMessage(content=message_content))

    async def astream(
        self,
        conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        safe_prompt: bool = False,
    ):
        formatted_messages = self._format_messages(conversation.history)
        client = mistralai.Mistral(api_key=self.api_key)

        stream_response = await client.chat.stream_async(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safe_prompt=safe_prompt,
        )
        message_content = ""

        for chunk in stream_response:
            if chunk.data.choices[0].delta.content:
                message_content += chunk.data.choices[0].delta.content
                yield chunk.data.choices[0].delta.content

        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                enable_json=enable_json,
                safe_prompt=safe_prompt,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
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
                    enable_json=enable_json,
                    safe_prompt=safe_prompt,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
