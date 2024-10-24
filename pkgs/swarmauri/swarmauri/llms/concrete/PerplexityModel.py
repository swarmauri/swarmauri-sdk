import asyncio
import json
import logging
from typing import List, Dict, Literal, Optional

import httpx
import requests
import aiohttp  # for async requests
from matplotlib.font_manager import json_dump
from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class PerplexityModel(LLMBase):
    """
    Provider resources: https://docs.perplexity.ai/guides/model-cards
    Link to deprecated models: https://docs.perplexity.ai/changelog/changelog#model-deprecation-notice
    """

    api_key: str
    allowed_models: List[str] = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-huge-128k-online",
        "llama-3.1-sonar-small-128k-chat",
        "llama-3.1-sonar-large-128k-chat",
        "llama-3.1-8b-instruct",
        "llama-3.1-70b-instruct",
    ]
    name: str = "llama-3.1-70b-instruct"
    type: Literal["PerplexityModel"] = "PerplexityModel"

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
        prompt_time: float = 0,
        completion_time: float = 0,
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
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ):
        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            response = requests.post(url, json=payload, headers=headers)

        result = response.json()
        message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ):
        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    result = await response.json()

        message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})
        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ):
        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stream": True,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            with requests.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                message_content = ""
                for chunk in response.iter_lines(decode_unicode=True):
                    json_string = chunk.replace("data: ", "", 1)
                    if json_string:
                        chunk_data = json.loads(json_string)
                        delta_content = (
                            chunk_data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        message_content += delta_content
                        yield delta_content

                        if chunk_data["usage"]:
                            usage_data = chunk_data["usage"]

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ):
        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stream": True,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=None
                )
                message_content = ""
                usage_data = {}

                async for line in response.aiter_lines():
                    json_string = line.replace("data: ", "", 1)
                    if json_string:  # Ensure it's not empty
                        chunk_data = json.loads(json_string)
                        delta_content = (
                            chunk_data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        message_content += delta_content

                        yield delta_content

                        usage_data = chunk_data.get("usage", usage_data)

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ):
        return [
            self.predict(
                conversation=conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                return_citations=return_citations,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        max_concurrent: int = 5,  # Maximum concurrent tasks
    ):
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conversation=conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    return_citations=return_citations,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
