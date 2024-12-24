import json
from typing import AsyncIterator, Iterator, List, Dict, Literal
import httpx
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase
import asyncio

from swarmauri_standard.messages.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class GeminiProModel(LLMBase):
    """
    GeminiProModel is a class interface for interacting with the Gemini language model API.

    Attributes:
        api_key (str): API key for authentication with the Gemini API.
        allowed_models (List[str]): List of allowed model names for selection.
        name (str): Default name of the model in use.
        type (Literal): Type identifier for GeminiProModel.

    Provider resources: https://deepmind.google/technologies/gemini/pro/
    """

    api_key: str
    allowed_models: List[str] = ["gemini-1.5-pro", "gemini-1.5-flash"]
    name: str = "gemini-1.5-pro"
    type: Literal["GeminiProModel"] = "GeminiProModel"
    _safety_settings: List[Dict[str, str]] = PrivateAttr(
        [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]
    )

    _client: httpx.Client = PrivateAttr(
        default_factory=lambda: httpx.Client(
            base_url="https://generativelanguage.googleapis.com/v1beta/models",
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
    )
    _async_client: httpx.AsyncClient = PrivateAttr(
        default_factory=lambda: httpx.AsyncClient(
            base_url="https://generativelanguage.googleapis.com/v1beta/models",
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
    )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats messages for API payload compatibility.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of message objects.

        Returns:
            List[Dict[str, str]]: List of formatted message dictionaries.
        """
        message_properties = ["content", "role"]
        sanitized_messages = [
            message.model_dump(include=message_properties)
            for message in messages
            if message.role != "system"
        ]

        for message in sanitized_messages:
            if message["role"] == "assistant":
                message["role"] = "model"

            message["parts"] = message.pop("content")

        return [
            {"parts": [{"text": message["parts"]}]} for message in sanitized_messages
        ]

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        """
        Retrieves the system message content from a conversation.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of message objects with message history.

        Returns:
            str: Content of the system message, if present; otherwise, None.
        """
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        if system_context:
            return {"parts": {"text": system_context}}
        return None

    def _prepare_usage_data(
        self,
        usage_data: UsageData,
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
    ) -> UsageData:
        """
        Prepares and extracts usage data and response timing.
        """

        total_time = prompt_time + completion_time

        usage = UsageData(
            prompt_tokens=usage_data["promptTokenCount"],
            completion_tokens=usage_data["candidatesTokenCount"],
            total_tokens=usage_data["totalTokenCount"],
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 25,
    ) -> Conversation:
        """
        Generates a prediction for the given conversation using the specified parameters.

        Args:
            conversation (Conversation): The conversation object containing the history of messages.
            temperature (float, optional): The sampling temperature to use. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 256.

        Returns:
            Conversation: The updated conversation object with the new message added.

        Raises:
            httpx.HTTPStatusError: If the HTTP request to the generation endpoint fails.
        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        next_message = formatted_messages.pop()

        payload = {
            "contents": next_message,
            "generationConfig": generation_config,
            "safetySettings": self._safety_settings,
        }
        if system_context:
            payload["systemInstruction"] = system_context

        with DurationManager() as prompt_timer:
            response = self._client.post(
                f"/{self.name}:generateContent?key={self.api_key}", json=payload
            )
            response.raise_for_status()

        response_data = response.json()

        message_content = response_data["candidates"][0]["content"]["parts"][0]["text"]

        usage_data = response_data["usageMetadata"]

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Conversation:
        """
        Asynchronously generates a response for a given conversation using the GeminiProModel.

        Args:
            conversation (Conversation): The conversation object containing the history of messages.
            temperature (float, optional): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens in the generated response. Defaults to 256.

        Returns:
            Conversation: The updated conversation object with the generated response added.

        Raises:
            httpx.HTTPStatusError: If the HTTP request to the generation endpoint fails.
        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        next_message = formatted_messages.pop()

        payload = {
            "contents": next_message,
            "generationConfig": generation_config,
            "safetySettings": self._safety_settings,
        }
        if system_context:
            payload["systemInstruction"] = system_context

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(
                f"/{self.name}:generateContent?key={self.api_key}",
                json=payload,
            )
            response.raise_for_status()

        response_data = response.json()
        message_content = response_data["candidates"][0]["content"]["parts"][0]["text"]
        usage_data = response_data["usageMetadata"]

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Iterator[str]:
        """
        Streams the response from the model based on the given conversation.

        Args:
            conversation (Conversation): The conversation object containing the history of messages.
            temperature (float, optional): The temperature setting for the generation. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 256.

        Yields:
            str: Chunks of the generated response text.

        Raises:
            httpx.HTTPStatusError: If the HTTP request to the model fails.

        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        next_message = formatted_messages.pop()

        payload = {
            "contents": next_message,
            "generationConfig": generation_config,
            "safetySettings": self._safety_settings,
        }
        if system_context:
            payload["systemInstruction"] = system_context

        with DurationManager() as prompt_timer:
            response = self._client.post(
                f"/{self.name}:streamGenerateContent?alt=sse&key={self.api_key}",
                json=payload,
            )

            response.raise_for_status()

        full_response = ""
        with DurationManager() as completion_timer:
            for line in response.iter_lines():
                json_str = line.replace("data: ", "")
                if json_str:
                    response_data = json.loads(json_str)
                    chunk = response_data["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                    full_response += chunk
                    yield chunk

                    if "usageMetadata" in response_data:
                        usage_data = response_data["usageMetadata"]

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=full_response, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams generated content for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing the history of messages.
            temperature (float, optional): The temperature for the generation process. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 256.

        Yields:
            str: Chunks of generated content as they are received.

        Raises:
            httpx.HTTPStatusError: If the HTTP request to the generation service fails.

        """
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        next_message = formatted_messages.pop()

        payload = {
            "contents": next_message,
            "generationConfig": generation_config,
            "safetySettings": self._safety_settings,
        }
        if system_context:
            payload["systemInstruction"] = system_context

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(
                f"/{self.name}:streamGenerateContent?alt=sse&key={self.api_key}",
                json=payload,
            )
            response.raise_for_status()

        full_response = ""
        with DurationManager() as completion_timer:
            async for line in response.aiter_lines():
                json_str = line.replace("data: ", "")
                if json_str:
                    response_data = json.loads(json_str)
                    chunk = response_data["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                    full_response += chunk
                    yield chunk

                    if "usageMetadata" in response_data:
                        usage_data = response_data["usageMetadata"]

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=full_response, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> List:
        """
        Synchronously process multiple conversations.

        Args:
            conversations (List[Conversation]): A list of Conversation objects to be processed.
            temperature (float, optional): The sampling temperature to use. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 256.

        Returns:
            List: A list of predictions for each conversation.
        """
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        max_concurrent: int = 5,
    ) -> List:
        """
        Asynchronously processes a batch of conversations using the `apredict` method.

        Args:
            conversations (List[Conversation]): A list of Conversation objects to be processed.
            temperature (float, optional): The temperature parameter for the prediction. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the prediction. Defaults to 256.
            max_concurrent (int, optional): The maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List: A list of results from the `apredict` method for each conversation.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
