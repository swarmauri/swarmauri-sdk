import asyncio
import json
import logging
from typing import List, Optional, Dict, Literal, Any, Union, AsyncGenerator

from groq import Groq, AsyncGroq
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class GroqModel(LLMBase):
    """Provider resources: https://console.groq.com/docs/models"""

    api_key: str
    stream: Optional[bool] = False
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

    @staticmethod
    def _format_messages(
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

    @staticmethod
    async def _predict_async(
            client: Union[Groq, AsyncGroq],
            **kwargs
    ) -> AsyncGenerator[str, None]:
        response = await client.chat.completions.create(**kwargs)

        async for chunk in response:
            await asyncio.sleep(0.05)
            yield chunk.choices[0].delta.content

    @staticmethod
    def _predict_sync(
            client: Union[Groq, AsyncGroq],
            **kwargs
    ) -> str:
        response = client.chat.completions.create(**kwargs)

        result = json.loads(response.json())
        message_content = result["choices"][0]["message"]["content"]
        return message_content

    def predict(
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
            "stream": self.stream
        }

        if self.stream:
            client = AsyncGroq(api_key=self.api_key)
            return self._predict_async(client, **kwargs)
        else:
            client = Groq(api_key=self.api_key)
            message_content = self._predict_sync(client, **kwargs)
            conversation.add_message(AgentMessage(content=message_content))
            return conversation