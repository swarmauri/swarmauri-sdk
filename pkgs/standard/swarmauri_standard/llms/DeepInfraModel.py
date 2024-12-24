import json
from typing import List, Dict, Literal, AsyncIterator, Iterator
import httpx
import asyncio
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_core.typing import SubclassUnion

from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase


class DeepInfraModel(LLMBase):
    """
    A class for interacting with DeepInfra's model API for text generation.

    This implementation uses httpx for both synchronous and asynchronous HTTP requests,
    providing support for predictions, streaming responses, and batch processing.

    Attributes:
        api_key (str): DeepInfra API key for authentication
            Can be obtained from: https://deepinfra.com/dash/api_keys

        allowed_models (List[str]): List of supported model identifiers on DeepInfra
            Full list available at: https://deepinfra.com/models/text-generation

        name (str): The currently selected model name
            Defaults to "Qwen/Qwen2-72B-Instruct"

        type (Literal["DeepInfraModel"]): Type identifier for the model class

    Link to Allowed Models: https://deepinfra.com/models/text-generation
    Link to API KEY: https://deepinfra.com/dash/api_keys
    """

    _BASE_URL: str = PrivateAttr("https://api.deepinfra.com/v1/openai")
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)

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

    def __init__(self, **data):
        """
        Initializes the DeepInfraModel instance with the provided API key
        and sets up httpx clients for both sync and async operations.

        Args:
            **data: Keyword arguments for model initialization.
        """
        super().__init__(**data)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self._client = httpx.Client(
            headers=headers, base_url=self._BASE_URL, timeout=30
        )
        self._async_client = httpx.AsyncClient(
            headers=headers, base_url=self._BASE_URL, timeout=30
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats conversation history into a list of dictionaries suitable for API requests.

        Args:
            messages (List[SubclassUnion[MessageBase]]): The conversation history.

        Returns:
            List[Dict[str, str]]: Formatted message list.
        """
        message_properties = ["content", "role", "name"]
        return [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]

    def _create_request_payload(
        self,
        formatted_messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        enable_json: bool,
        stop: List[str] = None,
        stream: bool = False,
    ) -> Dict:
        """
        Creates the payload for the API request.

        Args:
            formatted_messages (List[Dict[str, str]]): Formatted messages for the conversation.
            temperature (float): Sampling temperature for the response.
            max_tokens (int): Maximum number of tokens to generate.
            enable_json (bool): Whether to enable JSON response format.
            stop (List[str], optional): Stop sequences.
            stream (bool): Whether to stream the response.

        Returns:
            Dict: Payload for the API request.
        """
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stream": stream,
        }

        if stop:
            payload["stop"] = stop

        if enable_json:
            payload["response_format"] = {"type": "json_object"}

        return payload

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = None,
    ):
        """
        Sends a synchronous request to generate a response from the model.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum number of tokens to generate.
            enable_json (bool): Flag for enabling JSON response format.
            stop (List[str], optional): Stop sequences for the response.

        Returns:
            Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._create_request_payload(
            formatted_messages, temperature, max_tokens, enable_json, stop
        )

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()

        result = response.json()
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = None,
    ):
        """
        Sends an asynchronous request to generate a response from the model.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum number of tokens to generate.
            enable_json (bool): Flag for enabling JSON response format.
            stop (List[str], optional): Stop sequences for the response.

        Returns:
            Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._create_request_payload(
            formatted_messages, temperature, max_tokens, enable_json, stop
        )

        response = await self._async_client.post("/chat/completions", json=payload)
        response.raise_for_status()

        result = response.json()
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        stop: List[str] = None,
    ) -> Iterator[str]:
        """
        Streams response content from the model synchronously.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum number of tokens to generate.
            stop (List[str], optional): Stop sequences for the response.

        Yields:
            str: Chunks of content from the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._create_request_payload(
            formatted_messages, temperature, max_tokens, False, stop, stream=True
        )

        with self._client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            collected_content = []

            for line in response.iter_lines():
                # Convert bytes to string if necessary
                if isinstance(line, bytes):
                    line = line.decode("utf-8")

                if line.startswith("data: "):
                    line = line[6:]  # Remove 'data: ' prefix
                    if line != "[DONE]":
                        chunk = json.loads(line)
                        if chunk["choices"][0]["delta"].get("content"):
                            content = chunk["choices"][0]["delta"]["content"]
                            collected_content.append(content)
                            yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        stop: List[str] = None,
    ) -> AsyncIterator[str]:
        """
        Streams response content from the model asynchronously.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum number of tokens to generate.
            stop (List[str], optional): Stop sequences for the response.

        Yields:
            str: Chunks of content from the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._create_request_payload(
            formatted_messages, temperature, max_tokens, False, stop, stream=True
        )

        async with self._async_client.stream(
            "POST", "/chat/completions", json=payload
        ) as response:
            response.raise_for_status()
            collected_content = []

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    line = line[6:]  # Remove 'data: ' prefix
                    if line != "[DONE]":
                        chunk = json.loads(line)
                        if chunk["choices"][0]["delta"].get("content"):
                            content = chunk["choices"][0]["delta"]["content"]
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
        """
        Processes multiple conversations in batch synchronously.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum number of tokens to generate.
            enable_json (bool): Flag for enabling JSON response format.
            stop (List[str], optional): Stop sequences for responses.

        Returns:
            List: List of updated conversations with model responses.
        """
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
        """
        Processes multiple conversations asynchronously, with concurrency control.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum number of tokens to generate.
            enable_json (bool): Flag for enabling JSON response format.
            stop (List[str], optional): Stop sequences for responses.
            max_concurrent (int): Maximum number of concurrent tasks.

        Returns:
            List: List of updated conversations with model responses.
        """
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
