import asyncio
import json
from pydantic import PrivateAttr
import httpx
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri.utils.duration_manager import DurationManager
from swarmauri_standard.conversations.Conversation import Conversation
from typing import List, Optional, Dict, Literal, Any, AsyncGenerator, Generator

from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase

from swarmauri_standard.messages.AgentMessage import UsageData


class OpenAIModel(LLMBase):
    """
    OpenAIModel class for interacting with the Groq language models API. This class
    provides synchronous and asynchronous methods to send conversation data to the
    model, receive predictions, and stream responses.

    Attributes:
        api_key (str): API key for authenticating requests to the Groq API.
        allowed_models (List[str]): List of allowed model names that can be used.
        name (str): The default model name to use for predictions.
        type (Literal["OpenAIModel"]): The type identifier for this class.


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
    _BASE_URL: str = PrivateAttr(default="https://api.openai.com/v1/chat/completions")
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data) -> None:
        """
        Initialize the OpenAIModel class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _format_messages(
        self,
        messages: List[SubclassUnion[MessageBase]],
    ) -> List[Dict[str, Any]]:
        """
        Formats conversation messages into the structure expected by the API.

        Args:
            messages (List[MessageBase]): List of message objects from the conversation history.

        Returns:
            List[Dict[str, Any]]: List of formatted message dictionaries.
        """

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
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
    ) -> UsageData:
        """
        Prepare usage data by combining token counts and timing information.

        Args:
            usage_data: Raw usage data containing token counts.
            prompt_time (float): Time taken for prompt processing.
            completion_time (float): Time taken for response completion.

        Returns:
            UsageData: Processed usage data.
        """
        total_time = prompt_time + completion_time

        # Filter usage data for relevant keys
        filtered_usage_data = {
            key: value
            for key, value in usage_data.items()
            if key
            not in {
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "prompt_time",
                "completion_time",
                "total_time",
            }
        }

        usage = UsageData(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
            **filtered_usage_data,
        )

        return usage

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Generates a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        with DurationManager() as promt_timer:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data, promt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Async method to generate a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        with DurationManager() as promt_timer:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data, promt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Generator[str, None, None]:
        """
        Streams response text from the model in real-time.

        Args:
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Yields:
            str: Partial response content from the model.
        """

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True,
            "stop": stop or [],
            "stream_options": {"include_usage": True},
        }
        if enable_json:
            payload["response_format"] = "json_object"

        with DurationManager() as promt_timer:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        message_content = ""
        usage_data = {}
        with DurationManager() as completion_timer:
            for line in response.iter_lines():
                json_str = line.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if chunk["choices"] and chunk["choices"][0]["delta"]:
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                        if "usage" in chunk and chunk["usage"] is not None:
                            usage_data = chunk["usage"]

                except json.JSONDecodeError:
                    pass

        usage = self._prepare_usage_data(
            usage_data, promt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that streams response text from the model in real-time.

        Args:
            conversation (Conversation): Conversation object with message history.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for the model's response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Yields:
            str: Partial response content from the model.
        """

        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True,
            "stop": stop or [],
            "stream_options": {"include_usage": True},
        }
        if enable_json:
            payload["response_format"] = "json_object"

        with DurationManager() as promt_timer:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        message_content = ""
        usage_data = {}
        with DurationManager() as completion_timer:
            async for line in response.aiter_lines():
                json_str = line.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if chunk["choices"] and chunk["choices"][0]["delta"]:
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                        if "usage" in chunk and chunk["usage"] is not None:
                            usage_data = chunk["usage"]
                except json.JSONDecodeError:
                    pass

        usage = self._prepare_usage_data(
            usage_data, promt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations and generates responses for each sequentially.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
        """
        results = []
        for conversation in conversations:
            result_conversation = self.predict(
                conversation,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                enable_json=enable_json,
                stop=stop,
            )
            results.append(result_conversation)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: float = 1.0,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
        max_concurrent=5,
    ) -> List[Conversation]:
        """
        Async method for processing a batch of conversations concurrently.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[Conversation]: List of updated conversations with model responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: Conversation) -> Conversation:
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
