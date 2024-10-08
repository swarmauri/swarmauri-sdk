import json
from pydantic import Field
import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
from openai import OpenAI, AsyncOpenAI
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


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
    client: OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)
    api_key: str

    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:

        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = [],
    ):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        - stop (List[str]): List of tokens at which to stop generation.
                being None causes some models to throw status 400
                 (*chatgpt-4o-latest*)

        Returns:
        - The generated message content.
        """
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(api_key=self.api_key)

        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop,
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop,
            )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = [],
    ):
        """Asynchronous version of predict"""
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

        response = await self.async_client.chat.completions.create(**kwargs)
        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def stream_predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        stop: List[str] = [],
    ) -> Iterator[str]:
        """Synchronously stream the response token by token"""
        formatted_messages = self._format_messages(conversation.history)

        stream = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            stop=stop,
        )

        collected_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def astream_predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        stop: List[str] = [],
    ) -> AsyncIterator[str]:
        """Asynchronously stream the response token by token"""
        formatted_messages = self._format_messages(conversation.history)

        stream = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            stop=stop,
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
    ) -> List:
        """Process multiple conversations in parallel"""
        tasks = [
            self.apredict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                enable_json=enable_json,
                stop=stop,
            )
            for conv in conversations
        ]
        return await asyncio.gather(*tasks)
