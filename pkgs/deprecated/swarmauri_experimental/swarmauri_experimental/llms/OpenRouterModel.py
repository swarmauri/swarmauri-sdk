import json
from typing import List, Dict, Literal, AsyncIterator, Iterator, Optional
from openai import OpenAI, AsyncOpenAI
from pydantic import Field
import asyncio
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class OpenRouterModel(LLMBase):
    """
    Provider resources: https://openrouter.ai/docs
    """

    api_key: str
    allowed_models: List[str] = [
        "ai21/jamba-1-5-large",
        "ai21/jamba-1-5-mini",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-haiku:beta",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-opus:beta",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-sonnet:beta",
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-sonnet:beta",
        "deepseek/deepseek-chat",
        "google/gemini-flash-1.5",
        # "google/gemini-flash-1.5-exp", # experimental model continues to report 429 errors
        # "google/gemini-flash-8b-1.5-exp", # experimental model continues to report 429 errors
        "google/gemini-pro",
        "google/gemini-pro-1.5",
        # "google/gemini-pro-1.5-exp", # experimental model continues to report 429 errors
        "google/gemini-pro-vision",
        "meta-llama/llama-3-70b-instruct",
        "meta-llama/llama-3.1-405b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mistral-7b-instruct",
        "mistralai/mistral-7b-instruct-v0.1",
        "mistralai/mistral-7b-instruct-v0.3",
        "mistralai/mistral-large",
        "mistralai/mistral-nemo",
        "mistralai/mistral-small",
        "mistralai/mixtral-8x22b-instruct",
        "mistralai/mixtral-8x7b-instruct",
        "mistralai/mixtral-8x7b-instruct:nitro",
        "openai/gpt-3.5-turbo",
        "openai/gpt-3.5-turbo-0125",
        "openai/gpt-3.5-turbo-0613",
        "openai/gpt-3.5-turbo-1106",
        "openai/gpt-3.5-turbo-16k",
        "openai/gpt-4",
        "openai/gpt-4-32k",
        "openai/gpt-4-1106-preview",
        "openai/gpt-4-turbo",
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4-vision-preview",
        "openai/gpt-4o",
        "openai/gpt-4o-2024-05-13",
        "openai/gpt-4o-2024-08-06",
        "openai/gpt-4o-extended",
        "openai/gpt-4o-mini",
        "openai/gpt-4o-mini-2024-07-18",
        "qwen/qwen-2.5-72b-instruct",
    ]
    name: str = "mistralai/mistral-7b-instruct-v0.1"
    type: Literal["OpenRouterModel"] = "OpenRouterModel"
    app_name: Optional[str] = None
    site_url: Optional[str] = None
    client: OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def _get_headers(self) -> Dict[str, str]:
        headers = {}
        if self.app_name:
            headers["X-Title"] = self.app_name
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        return headers

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _get_openai_compatible_params(self, **kwargs) -> Dict:
        # Define which parameters are supported by the OpenAI client
        openai_params = {
            "model": kwargs.get("model"),
            "messages": kwargs.get("messages"),
            "temperature": kwargs.get("temperature"),
            "max_tokens": kwargs.get("max_tokens"),
            "top_p": kwargs.get("top_p"),
            "frequency_penalty": kwargs.get("frequency_penalty"),
            "presence_penalty": kwargs.get("presence_penalty"),
            "response_format": kwargs.get("response_format"),
            "stream": kwargs.get("stream", False),
        }

        # Remove None values
        return {k: v for k, v in openai_params.items() if v is not None}

    def predict(
        self,
        conversation,
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = None,  # Made optional
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = None,  # Made optional
        min_p: Optional[float] = None,  # Made optional
        top_a: Optional[float] = None,  # Made optional
        response_format: Optional[Dict[str, str]] = None,
    ):
        formatted_messages = self._format_messages(conversation.history)

        params = self._get_openai_compatible_params(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            response_format=response_format,
        )

        response = self.client.chat.completions.create(
            **params,
            extra_headers=self._get_headers(),
        )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def apredict(
        self,
        conversation,
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = None,
        min_p: Optional[float] = None,
        top_a: Optional[float] = None,
        response_format: Optional[Dict[str, str]] = None,
    ):
        formatted_messages = self._format_messages(conversation.history)

        params = self._get_openai_compatible_params(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            response_format=response_format,
        )

        response = await self.async_client.chat.completions.create(
            **params,
            extra_headers=self._get_headers(),
        )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def stream(
        self,
        conversation,
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = None,
        min_p: Optional[float] = None,
        top_a: Optional[float] = None,
    ) -> Iterator[str]:
        formatted_messages = self._format_messages(conversation.history)

        params = self._get_openai_compatible_params(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=True,
        )

        stream = self.client.chat.completions.create(
            **params,
            extra_headers=self._get_headers(),
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
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = None,
        min_p: Optional[float] = None,
        top_a: Optional[float] = None,
    ) -> AsyncIterator[str]:
        formatted_messages = self._format_messages(conversation.history)

        params = self._get_openai_compatible_params(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=True,
        )

        stream = await self.async_client.chat.completions.create(
            **params,
            extra_headers=self._get_headers(),
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
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = None,
        min_p: Optional[float] = None,
        top_a: Optional[float] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> List:
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                repetition_penalty=repetition_penalty,
                min_p=min_p,
                top_a=top_a,
                response_format=response_format,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature: float = 1.0,
        max_tokens: Optional[int] = 256,
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = None,
        min_p: Optional[float] = None,
        top_a: Optional[float] = None,
        response_format: Optional[Dict[str, str]] = None,
        max_concurrent: int = 5,
    ) -> List:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    repetition_penalty=repetition_penalty,
                    min_p=min_p,
                    top_a=top_a,
                    response_format=response_format,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
