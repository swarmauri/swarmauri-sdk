import logging
import json
import asyncio
import aiohttp
from typing import List, Dict, Literal, AsyncIterator, Iterator
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

import requests


class ShuttleAIModel(LLMBase):
    api_key: str
    allowed_models: List[str] = [
        # "alibaba-cloud/qwen-2.5-72b-instruct",
        # "alibaba-cloud/qwen-2.5-coder-7b",
        # "alibaba-cloud/qwen-2.5-math-72b",
        # "anthropic/claude-3-haiku-20240307",
        # "anthropic/claude-3-opus-20240229",
        # "anthropic/claude-3.5-sonnet-20240620",
        # "cohere/command-r",
        # "cohere/command-r-08-2024",
        # "cohere/command-r-plus",
        # "cohere/command-r-plus-08-2024",
        # "google/gemini-1.5-flash",
        # #'google/gemini-1.5-flash-8b-exp-0827',
        # #'google/gemini-1.5-flash-exp-0827',
        # "google/gemini-1.5-pro",
        # #'google/gemini-1.5-pro-exp-0827',
        # "mattshumer/reflection-llama-3.1-70b",
        # "meta-llama/meta-llama-3.1-405b-instruct",
        # "meta-llama/meta-llama-3.1-70b-instruct",
        # "meta-llama/meta-llama-3.1-8b-instruct",
        # "mistralai/codestral-2405",
        # "mistralai/mistral-nemo-instruct-2407",
        # "openai/chatgpt-4o-latest",
        # "openai/gpt-3.5-turbo-0125",
        # "openai/gpt-3.5-turbo-1106",
        # "openai/gpt-4-0125-preview",
        # "openai/gpt-4-0613",
        # "openai/gpt-4-turbo-2024-04-09",
        # "openai/gpt-4o-2024-05-13",
        # "openai/gpt-4o-2024-08-06",
        # "openai/gpt-4o-mini-2024-07-18",
        # "openai/o1-mini-2024-09-12",
        # "openai/o1-preview-2024-09-12",
        # "perplexity/llama-3.1-sonar-large-128k-chat",
        # "perplexity/llama-3.1-sonar-large-128k-online",
        # "perplexity/llama-3.1-sonar-small-128k-chat",
        # "perplexity/llama-3.1-sonar-small-128k-online",
        # "shuttleai/s1",
        # "shuttleai/s1-mini",
        "shuttleai/shuttle-3",
        # "shuttleai/shuttle-3-mini",
    ]

    name: str = "shuttleai/shuttle-3"

    type: Literal["ShuttleAIModel"] = "ShuttleAIModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties) for message in messages
        ]
        return formatted_messages

    def _prepare_payload(
        self,
        formatted_messages,
        temperature,
        max_tokens,
        top_p,
        internet,
        citations,
        tone,
        raw,
        image,
        stream=False,
    ):
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        if raw:
            payload["raw"] = True
        if internet:
            payload["internet"] = True
        if image is not None:
            payload["image"] = image
        if self.name in ["gpt-4-bing", "gpt-4-turbo-bing"]:
            payload["tone"] = tone
            if citations:
                payload["citations"] = True
        if stream:
            payload["stream"] = True

        return payload

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
    ):
        formatted_messages = self._format_messages(conversation.history)
        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = self._prepare_payload(
            formatted_messages,
            temperature,
            max_tokens,
            top_p,
            internet,
            citations,
            tone,
            raw,
            image,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logging.info(f"Payload being sent: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        logging.info(f"Response received: {response.text}")

        try:
            message_content = response.json()["choices"][0]["message"]["content"]
        except KeyError as e:
            logging.info(f"Error parsing response: {response.text}")
            raise e

        conversation.add_message(AgentMessage(content=message_content))
        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
    ):
        formatted_messages = self._format_messages(conversation.history)
        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = self._prepare_payload(
            formatted_messages,
            temperature,
            max_tokens,
            top_p,
            internet,
            citations,
            tone,
            raw,
            image,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response_json = await response.json()

        message_content = response_json["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
    ) -> Iterator[str]:
        formatted_messages = self._format_messages(conversation.history)
        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = self._prepare_payload(
            formatted_messages,
            temperature,
            max_tokens,
            top_p,
            internet,
            citations,
            tone,
            raw,
            image,
            stream=True,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers, stream=True)

        collected_content = []
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8").split("data: ", 1)[-1])
                    if (
                        chunk.get("choices")
                        and chunk["choices"][0].get("delta")
                        and chunk["choices"][0]["delta"].get("content")
                    ):
                        content = chunk["choices"][0]["delta"]["content"]
                        collected_content.append(content)
                        yield content
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
    ) -> AsyncIterator[str]:
        formatted_messages = self._format_messages(conversation.history)
        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = self._prepare_payload(
            formatted_messages,
            temperature,
            max_tokens,
            top_p,
            internet,
            citations,
            tone,
            raw,
            image,
            stream=True,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                collected_content = []
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(
                                line.decode("utf-8").split("data: ", 1)[-1]
                            )
                            if (
                                chunk.get("choices")
                                and chunk["choices"][0].get("delta")
                                and chunk["choices"][0]["delta"].get("content")
                            ):
                                content = chunk["choices"][0]["delta"]["content"]
                                collected_content.append(content)
                                yield content
                        except json.JSONDecodeError:
                            continue  # Skip invalid JSON lines
                    await asyncio.sleep(0)  # Allow other tasks to run

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
    ) -> List:
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                internet=internet,
                citations=citations,
                tone=tone,
                raw=raw,
                image=image,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        internet=False,
        citations=False,
        tone="precise",
        raw=False,
        image=None,
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
                    internet=internet,
                    citations=citations,
                    tone=tone,
                    raw=raw,
                    image=image,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
