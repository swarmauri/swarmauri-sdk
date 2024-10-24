import asyncio
import json
from swarmauri.conversations.concrete.Conversation import Conversation
from typing import List, Optional, Dict, Literal, Any, Union, AsyncGenerator

from groq import Groq, AsyncGroq
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.messages.concrete.AgentMessage import UsageData


class GroqModel(LLMBase):
    """Provider resources: https://console.groq.com/docs/models"""

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
        # multimodal models
        "llama-3.2-11b-vision-preview",
    ]
    name: str = "gemma-7b-it"
    type: Literal["GroqModel"] = "GroqModel"

    def _format_messages(
        self,
        messages: List[SubclassUnion[MessageBase]],
    ) -> List[Dict[str, Any]]:
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
    ):
        """
        Prepares and extracts usage data and response timing.
        """

        usage = UsageData.model_validate(usage_data)
        return usage

    def predict(
        self,
        conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ):

        formatted_messages = self._format_messages(conversation.history)
        response_format = {"type": "json_object"} if enable_json else None

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "response_format": response_format,
            "stop": stop or [],
        }

        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(**kwargs)

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(usage_data)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    async def apredict(
        self,
        conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Union[str, AsyncGenerator[str, None]]:

        formatted_messages = self._format_messages(conversation.history)
        response_format = {"type": "json_object"} if enable_json else None

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "response_format": response_format,
            "stop": stop or [],
        }

        client = AsyncGroq(api_key=self.api_key)
        response = await client.chat.completions.create(**kwargs)

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(usage_data)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    def stream(
        self,
        conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Union[str, AsyncGenerator[str, None]]:

        formatted_messages = self._format_messages(conversation.history)
        response_format = {"type": "json_object"} if enable_json else None

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "response_format": response_format,
            "stream": True,
            "stop": stop or [],
            # "stream_options": {"include_usage": True},
        }

        client = Groq(api_key=self.api_key)
        stream = client.chat.completions.create(**kwargs)
        message_content = ""
        # usage_data = {}

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                message_content += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

                # if hasattr(chunk, "usage") and chunk.usage is not None:
                #     usage_data = chunk.usage

        # usage = self._prepare_usage_data(usage_data)

        conversation.add_message(AgentMessage(content=message_content))

    async def astream(
        self,
        conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:

        formatted_messages = self._format_messages(conversation.history)
        response_format = {"type": "json_object"} if enable_json else None

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "response_format": response_format,
            "stop": stop or [],
            "stream": True,
            # "stream_options": {"include_usage": True},
        }

        client = AsyncGroq(api_key=self.api_key)
        stream = await client.chat.completions.create(**kwargs)

        message_content = ""
        # usage_data = {}

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                message_content += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

                # if hasattr(chunk, "usage") and chunk.usage is not None:
                #     usage_data = chunk.usage

        # usage = self._prepare_usage_data(usage_data)
        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                enable_json=enable_json,
                stop=stop,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
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
                    top_p=top_p,
                    enable_json=enable_json,
                    stop=stop,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
