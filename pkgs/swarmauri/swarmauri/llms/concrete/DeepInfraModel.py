import json
from typing import List, Dict, Literal, AsyncIterator, Iterator
from openai import OpenAI, AsyncOpenAI
from pydantic import Field
import asyncio
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class DeepInfraModel(LLMBase):
    """
    Provider resources: https://deepinfra.com/models/text-generation
    """

    api_key: str
    allowed_models: List[str] = [
        "01-ai/Yi-34B-Chat",
        "Gryphe/MythoMax-L2-13b",  # not consistent with results
        "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1",
        "Phind/Phind-CodeLlama-34B-v2",
        "Qwen/Qwen2-72B-Instruct",
        "Qwen/Qwen2-7B-Instruct",
        "Qwen/Qwen2.5-72B-Instruct",
        "Sao10K/L3-70B-Euryale-v2.1",
        "Sao10K/L3.1-70B-Euryale-v2.2",
        "bigcode/starcoder2-15b",
        "bigcode/starcoder2-15b-instruct-v0.1",
        "codellama/CodeLlama-34b-Instruct-hf",
        "codellama/CodeLlama-70b-Instruct-hf",
        "cognitivecomputations/dolphin-2.6-mixtral-8x7b",
        "cognitivecomputations/dolphin-2.9.1-llama-3-70b",
        "databricks/dbrx-instruct",
        "google/codegemma-7b-it",
        "google/gemma-1.1-7b-it",
        "google/gemma-2-27b-it",
        "google/gemma-2-9b-it",
        "lizpreciatior/lzlv_70b_fp16_hf",  # not consistent with results
        "mattshumer/Reflection-Llama-3.1-70B",
        "mattshumer/Reflection-Llama-3.1-70B",
        "meta-llama/Llama-2-13b-chat-hf",
        "meta-llama/Llama-2-70b-chat-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Meta-Llama-3-70B-Instruct",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "meta-llama/Meta-Llama-3.1-405B-Instruct",
        "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "microsoft/Phi-3-medium-4k-instruct",
        "microsoft/WizardLM-2-7B",
        "microsoft/WizardLM-2-8x22B",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mistral-7B-Instruct-v0.2",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "mistralai/Mistral-Nemo-Instruct-2407",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "mistralai/Mixtral-8x22B-v0.1",
        "mistralai/Mixtral-8x22B-v0.1",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "nvidia/Nemotron-4-340B-Instruct",
        "openbmb/MiniCPM-Llama3-V-2_5",
        "openchat/openchat-3.6-8b",
        "openchat/openchat_3.5",  # not compliant with system context
        # "deepinfra/airoboros-70b", # deprecated: https://deepinfra.com/deepinfra/airoboros-70b
        #  'Gryphe/MythoMax-L2-13b-turbo', # deprecated: https://deepinfra.com/Gryphe/MythoMax-L2-13b-turbo/api
        # "Austism/chronos-hermes-13b-v2",  # deprecating: https://deepinfra.com/Austism/chronos-hermes-13b-v2/api
    ]

    name: str = "Qwen/Qwen2-72B-Instruct"
    type: Literal["DeepInfraModel"] = "DeepInfraModel"
    client: OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI(
            api_key=self.api_key, base_url="https://api.deepinfra.com/v1/openai"
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key, base_url="https://api.deepinfra.com/v1/openai"
        )

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
        stop: List[str] = None,
    ):
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

        response = self.client.chat.completions.create(**kwargs)

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
        stop: List[str] = None,
    ):
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

    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        stop: List[str] = None,
    ) -> Iterator[str]:
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

    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        stop: List[str] = None,
    ) -> AsyncIterator[str]:
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
        stop: List[str] = None,
    ) -> List:
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
        stop: List[str] = None,
        max_concurrent=5,
    ) -> List:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    enable_json=enable_json,
                    stop=stop,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
