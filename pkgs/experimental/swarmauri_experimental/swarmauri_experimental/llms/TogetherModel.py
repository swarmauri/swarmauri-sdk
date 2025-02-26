import warnings
import json
import httpx
import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
from pydantic import PrivateAttr

from swarmauri_standard.utils.retry_decorator import retry_on_status_codes
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(LLMBase, 'TogetherModel')
class TogetherModel(LLMBase):
    """
    A class for interacting with Together.xyz's model API for text generation.

    This implementation uses httpx for both synchronous and asynchronous HTTP requests,
    providing support for predictions, streaming responses, and batch processing.

    Attributes:
        api_key (str): Together API key for authentication
            See https://together.xyz/ for details.

        allowed_models (List[str]): List of known/supported model identifiers on Together.
            This is optional—can be removed or replaced.

        name (str): The currently selected model name
            Defaults to "deepseek-ai/DeepSeek-R1".

        type (Literal["TogetherModel"]): Type identifier for the model class.
    """

    _BASE_URL: str = PrivateAttr("https://api.together.xyz/v1/chat/completions")
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)

    api_key: str
    allowed_models: List[str] = [
        # Example known models on Together
        "deepseek-ai/DeepSeek-R1",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "meta-llama/Llama-2-70b-chat-hf",
    ]

    name: str = "deepseek-ai/DeepSeek-R1"
    type: Literal["TogetherModel"] = "TogetherModel"

    def __init__(self, **data):
        """
        Initializes the TogetherModel instance with the provided API key
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
            headers=headers, timeout=30
        )
        self._async_client = httpx.AsyncClient(
            headers=headers, timeout=30
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats conversation history into a list of dictionaries suitable for the Together API requests.

        Args:
            messages (List[SubclassUnion[MessageBase]]): The conversation history.

        Returns:
            List[Dict[str, str]]: Formatted message list.
        """
        # The structure typically follows the OpenAI Chat format: 
        # each item => { "role": "user"/"assistant"/"system", "content": "..."}
        # If your internal messages differ, adjust accordingly.
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
        top_p: float = 1.0,
        top_k: int = 50,
        repetition_penalty: float = 1.0,
    ) -> Dict:
        """
        Creates the payload for the Together API request.

        Args:
            formatted_messages (List[Dict[str, str]]): Formatted messages for the conversation.
            temperature (float): Sampling temperature for the response.
            max_tokens (int): Maximum number of tokens to generate.
            enable_json (bool): Whether to request a JSON-like response. 
                               (Not specifically used in Together, but you could adjust the prompt accordingly.)
            stop (List[str], optional): Stop sequences.
            stream (bool): Whether to stream the response.
            top_p (float): Nucleus sampling parameter.
            top_k (int): k for top-k sampling.
            repetition_penalty (float): Repetition penalty.

        Returns:
            Dict: Payload for the API request.
        """
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            # If max_tokens is None or 0, we can pass null. Otherwise pass the integer.
            "max_tokens": max_tokens if max_tokens else None,
            "stop": stop,
            "stream": stream,
        }

        # If you want a JSON-specific format in the response, 
        # you might handle that at the prompt-level or with system instructions.

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
            enable_json (bool): Not explicitly used in Together but left for consistency.
            stop (List[str], optional): Stop sequences for the response.

        Returns:
            Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._create_request_payload(
            formatted_messages, temperature, max_tokens, enable_json, stop
        )

        response = self._client.post(self._BASE_URL, json=payload)
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
            enable_json (bool): Not explicitly used in Together but left for consistency.
            stop (List[str], optional): Stop sequences for the response.

        Returns:
            Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = self._create_request_payload(
            formatted_messages, temperature, max_tokens, enable_json, stop
        )

        response = await self._async_client.post(self._BASE_URL, json=payload)
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
            formatted_messages, temperature, max_tokens, enable_json=False, stop=stop, stream=True
        )

        with self._client.stream("POST", self._BASE_URL, json=payload) as response:
            response.raise_for_status()
            collected_content = []

            for line in response.iter_lines():
                if not line:
                    continue
                if isinstance(line, bytes):
                    line = line.decode("utf-8")

                # Together.xyz typically sends streamed data with 'data: ' lines,
                # similar to OpenAI's style. Confirm in practice or via docs.
                if line.startswith("data: "):
                    line = line[6:]  # Remove 'data: '
                    if line.strip() == "[DONE]":
                        break
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
            formatted_messages, temperature, max_tokens, enable_json=False, stop=stop, stream=True
        )

        async with self._async_client.stream("POST", self._BASE_URL, json=payload) as response:
            response.raise_for_status()
            collected_content = []

            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                    if line.strip() == "[DONE]":
                        break
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
            enable_json (bool): Not explicitly used in Together but left for consistency.
            stop (List[str], optional): Stop sequences for the responses.

        Returns:
            List: Updated conversations with model responses.
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
            enable_json (bool): Not explicitly used in Together but left for consistency.
            stop (List[str], optional): Stop sequences for the responses.
            max_concurrent (int): Maximum number of concurrent tasks.

        Returns:
            List: Updated conversations with model responses.
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
