import asyncio
import json
from typing import List, Literal, Dict
import mistralai
from anyio import sleep
import logging
from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


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
            if message.role != "assistant"
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
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ):
        formatted_messages = self._format_messages(conversation.history)
        client = mistralai.Mistral(api_key=self.api_key)

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "safe_prompt": safe_prompt,
        }

        if enable_json:
            kwargs["response_format"] = {"type": "json_object"}

        with DurationManager() as prompt_timer:
            response = client.chat.complete(**kwargs)

        with DurationManager() as completion_timer:
            result = json.loads(response.model_dump_json())
            message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

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

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "safe_prompt": safe_prompt,
        }

        if enable_json:
            kwargs["response_format"] = {"type": "json_object"}

        with DurationManager() as prompt_timer:
            response = await client.chat.complete_async(**kwargs)
            await sleep(0.2)

        with DurationManager() as completion_timer:
            result = json.loads(response.model_dump_json())
            message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

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

        with DurationManager() as prompt_timer:
            stream_response = client.chat.stream(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )

        message_content = ""
        usage_data = {}

        with DurationManager() as completion_timer:
            for chunk in stream_response:
                if chunk.data.choices[0].delta.content:
                    message_content += chunk.data.choices[0].delta.content
                    yield chunk.data.choices[0].delta.content

                if hasattr(chunk.data, "usage") and chunk.data.usage is not None:
                    usage_data = chunk.data.usage

        usage = self._prepare_usage_data(
            usage_data.model_dump(), prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

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

        with DurationManager() as prompt_timer:
            stream_response = await client.chat.stream_async(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt,
            )

        usage_data = {}
        message_content = ""

        with DurationManager() as completion_timer:
            async for chunk in stream_response:
                if chunk.data.choices[0].delta.content:
                    message_content += chunk.data.choices[0].delta.content
                    yield chunk.data.choices[0].delta.content

                if hasattr(chunk.data, "usage") and chunk.data.usage is not None:
                    usage_data = chunk.data.usage

        usage = self._prepare_usage_data(
            usage_data.model_dump(), prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

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
