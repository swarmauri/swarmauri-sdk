import json
from typing import List, Dict, Literal, AsyncIterator, Iterator
import asyncio
import httpx
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase


class DeepSeekModel(LLMBase):
    """
    A client class for interfacing with DeepSeek's language model for chat completions.

    This class provides methods for synchronous and asynchronous prediction, streaming, and batch processing.
    It handles message formatting, payload construction, and response parsing to seamlessly integrate
    with the DeepSeek API.

    Attributes:
        api_key (str): The API key for authenticating with DeepSeek.
        allowed_models (List[str]): List of models supported by DeepSeek, defaulting to ["deepseek-chat"].
        name (str): The model name, defaulting to "deepseek-chat".
        type (Literal): The class type for identifying the LLM, set to "DeepSeekModel".

    Link to Allowed Models: https://platform.deepseek.com/api-docs/quick_start/pricing
    Link to API KEY: https://platform.deepseek.com/api_keys
    """

    _BASE_URL: str = PrivateAttr("https://api.deepseek.com/v1")

    api_key: str
    allowed_models: List[str] = ["deepseek-chat"]
    name: str = "deepseek-chat"
    type: Literal["DeepSeekModel"] = "DeepSeekModel"
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )
        self._async_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats a list of message objects into a list of dictionaries for API payload.

        Args:
            messages (List[SubclassUnion[MessageBase]]): The conversation history to format.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties) for message in messages
        ]
        return formatted_messages

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ):
        """
        Sends a synchronous request to the DeepSeek API to generate a chat response.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Returns:
            Updated conversation object with the generated response added.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "messages": formatted_messages,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "response_format": {"type": "text"},
            "stop": stop,
            "top_p": top_p,
        }
        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        message_content = response.json()["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ):
        """
        Sends an asynchronous request to the DeepSeek API to generate a chat response.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Returns:
            Updated conversation object with the generated response added.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "messages": formatted_messages,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "response_format": {"type": "text"},
            "stop": stop,
            "top_p": top_p,
        }
        response = await self._async_client.post("/chat/completions", json=payload)
        response.raise_for_status()
        message_content = response.json()["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> Iterator[str]:
        """
        Streams the response token by token synchronously from the DeepSeek API.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Yields:
            str: Token of the response being streamed.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "messages": formatted_messages,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "response_format": {"type": "text"},
            "stop": stop,
            "top_p": top_p,
            "stream": True,
        }
        with self._client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            collected_content = []
            for line in response.iter_lines():
                json_str = line.replace("data: ", "")
                if json_str:
                    try:
                        chunk = json.loads(json_str)
                        if chunk["choices"][0]["delta"]["content"]:
                            content = chunk["choices"][0]["delta"]["content"]
                            collected_content.append(content)
                            yield content
                    except json.JSONDecodeError:
                        pass

            full_content = "".join(collected_content)
            conversation.add_message(AgentMessage(content=full_content))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response token by token from the DeepSeek API.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Yields:
            str: Token of the response being streamed.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "messages": formatted_messages,
            "model": self.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "response_format": {"type": "text"},
            "stop": stop,
            "top_p": top_p,
            "stream": True,
        }
        async with self._async_client.stream(
            "POST", "/chat/completions", json=payload
        ) as response:
            response.raise_for_status()
            collected_content = []
            async for line in response.aiter_lines():
                json_str = line.replace("data: ", "")
                if json_str:
                    try:
                        chunk = json.loads(json_str)
                        if chunk["choices"][0]["delta"]["content"]:
                            content = chunk["choices"][0]["delta"]["content"]
                            collected_content.append(content)
                            yield content
                    except json.JSONDecodeError:
                        pass

            full_content = "".join(collected_content)
            conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> List:
        """
        Processes multiple conversations synchronously in a batch.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Returns:
            List: List of updated conversation objects with responses added.
        """
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                top_p=top_p,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
        max_concurrent=5,
    ) -> List:
        """
        Processes multiple conversations asynchronously in parallel, with concurrency control.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.
            max_concurrent (int): Maximum number of concurrent tasks allowed.

        Returns:
            List: List of updated conversation objects with responses added.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop,
                    top_p=top_p,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
