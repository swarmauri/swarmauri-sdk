import logging
from typing import Any, Dict, List, Optional, Type

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.messages.MessageBase import MessageBase
<<<<<<< HEAD
=======
from typing_extensions import Literal
>>>>>>> upstream/mono/dev

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.utils.duration_manager import DurationManager
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(LLMBase, "OpenAIReasonModel")
class OpenAIReasonModel(LLMBase):
    """
    OpenAIReasonModel class for interacting with the OpenAI Reasoning Model language models API. This class
    provides synchronous and asynchronous methods to send conversation data to the
    model, receive predictions, and stream responses.

    Attributes:
        api_key (SecretStr): API key for authenticating requests to the Groq API.
        allowed_models (List[str]): List of allowed model names that can be used.
        name (str): The default model name to use for predictions.
        type (Literal["OpenAIReasonModel"]): The type identifier for this class.
        timeout (float): Timeout duration for API requests.
        _BASE_URL (str): Base URL for the OpenAI API.
        _headers (Dict[str, str]): Headers for API requests.

    Provider resources: https://platform.openai.com/docs/models
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        "o3-deep-research-2025-06-26",
        "o4-mini-deep-research-2025-06-26",
        "o3-pro-2025-06-10",
        "o3-2025-04-16",
        "o4-mini-2025-04-16",
        "o1-pro-2025-03-19",
        "o1-mini",
        "o1",
        "o1-2024-12-17",
        "o1-mini-2024-09-12",
        "o3-mini",
        "o3-mini-2025-01-31",
    ]
    name: str = "o1-mini"
    type: Literal["OpenAIReasonModel"] = "OpenAIReasonModel"
    timeout: float = 600.0
    _BASE_URL: str = PrivateAttr(default="https://api.openai.com/v1/chat/completions")
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Initialize the OpenAIModel class with the provided data.

        Args:
            **data (Dict[str, Any]): Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    def _format_messages(
        self,
        messages: List[Type[MessageBase]],
    ) -> List[Dict[str, Any]]:
        """
        Formats conversation messages into the structure expected by the API.

        Args:
            messages (List[Type[MessageBase]]): List of message objects from the conversation history.

        Returns:
            List[Dict[str, Any]]: List of formatted message dictionaries.
        """

        formatted_messages = []
        for message in messages:
            formatted_message = message.model_dump(
                include=["content", "role", "name"], exclude_none=True
            )
            if message.role == "system" and self.name != "o1":
                raise ValueError(
                    "System messages are not allowed for models other than 'o1'."
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
        usage_data: UsageData,
        prompt_time: float = 0.0,
        completion_time: float = 0.0,
    ) -> UsageData:
        """
        Prepare usage data by combining token counts and timing information.

        Args:
            usage_data (UsageData): Raw usage data containing token counts.
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
        max_completion_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Generates a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message history.
            max_completion_tokens (int): Maximum tokens for the model's response.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_completion_tokens": max_completion_tokens,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        with DurationManager() as promt_timer:
            with httpx.Client(timeout=self.timeout) as client:
                logging.info(f"headers: {self._headers}")
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        if self.include_usage and usage_data:
            usage = self._prepare_usage_data(usage_data, promt_timer.duration)
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        max_completion_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> Conversation:
        """
        Async method to generate a response from the model based on the given conversation.

        Args:
            conversation (Conversation): Conversation object with message history.
            max_completion_tokens (int): Maximum tokens for the model's response.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            Conversation: Updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_completion_tokens": max_completion_tokens,
            "stop": stop or [],
        }
        if enable_json:
            payload["response_format"] = "json_object"

        with DurationManager() as prompt_timer:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        if self.include_usage and usage_data:
            usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def get_allowed_models(self) -> List[str]:
        """
        Queries the LLMProvider API endpoint to retrieve the list of allowed models.

        Returns:
            List[str]: List of allowed model names.
        """
        models_data = [
            "o1-mini",
            "o1",
            "o1-2024-12-17",
            "o1-mini-2024-09-12",
            "o3-mini",
            "o3-mini-2025-01-31",
        ]
        return models_data

    def stream(
        self,
        conversation: Conversation,
        max_completion_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> None:
        """
        Not implemented.

        Args:
            conversation (Conversation): Conversation object with message history.
            max_completion_tokens (int): Maximum tokens for the model's response.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError

    async def astream(
        self,
        conversation: Conversation,
        max_completion_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> None:
        """
        Not implemented.

        Args:
            conversation (Conversation): Conversation object with message history.
            max_completion_tokens (int): Maximum tokens for the model's response.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError

    def batch(
        self,
        conversations: List[Conversation],
        max_completion_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> None:
        """
        Not implemented.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            max_completion_tokens (int): Maximum tokens for the model's response.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError

    async def abatch(
        self,
        conversations: List[Conversation],
        max_completion_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
    ) -> None:
        """
        Not implemented.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            max_completion_tokens (int): Maximum tokens for the model's response.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError
