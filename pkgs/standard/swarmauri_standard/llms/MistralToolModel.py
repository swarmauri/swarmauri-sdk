import asyncio
import json
import logging
from typing import AsyncIterator, Iterator, List, Literal, Dict, Any
import httpx
from pydantic import PrivateAttr
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.MistralSchemaConverter import (
    MistralSchemaConverter,
)
from swarmauri.utils.retry_decorator import retry_on_status_codes


class MistralToolModel(LLMBase):
    """
    A model class for interacting with the Mistral API for tool-assisted conversation and prediction.

    This class provides methods for synchronous and asynchronous communication with the Mistral API.
    It supports processing single and batch conversations, as well as streaming responses.

    Attributes:
        api_key (str): The API key for authenticating requests with the Mistral API.
        allowed_models (List[str]): A list of supported model names for the Mistral API.
        name (str): The default model name to use for predictions.
        type (Literal["MistralToolModel"]): The type identifier for the model.

    Provider resources: https://docs.mistral.ai/capabilities/function_calling/#available-models
    """

    api_key: str
    allowed_models: List[str] = [
        "open-mixtral-8x22b",
        "mistral-small-latest",
        "mistral-large-latest",
        "open-mistral-nemo",
    ]
    name: str = "open-mixtral-8x22b"
    type: Literal["MistralToolModel"] = "MistralToolModel"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.mistral.ai/v1/chat/completions")

    def __init__(self, **data) -> None:
        """
        Initializes the GroqToolModel instance, setting up headers for API requests.

        Parameters:
            **data: Arbitrary keyword arguments for initialization.
        """
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

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        """
        Convert a dictionary of tools to the schema format required by Mistral API.

        Args:
            tools (dict): A dictionary of tool objects.

        Returns:
            List[Dict[str, Any]]: A list of converted tool schemas.
        """
        return [MistralSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history messages for the Mistral API.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of message objects from the conversation history.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """
        message_properties = ["content", "role", "name", "tool_call_id"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "assistant"
        ]
        logging.info(formatted_messages)
        return formatted_messages

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        safe_prompt: bool = False,
    ) -> Conversation:
        """
        Make a synchronous prediction using the Mistral API.

        Args:
            conversation (Conversation): The conversation object.
            toolkit (Optional): The toolkit for tool assistance.
            tool_choice (Optional): The tool choice strategy (default is "auto").
            temperature (float): The temperature for response variability.
            max_tokens (int): The maximum number of tokens for the response.
            safe_prompt (bool): Whether to use a safer prompt.

        Returns:
            Conversation: The updated conversation object.
        """
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice,
            "safe_prompt": safe_prompt,
        }

        response = self._client.post(self._BASE_URL, json=payload)

        response.raise_for_status()

        tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )

        payload["messages"] = messages

        response = self._client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        agent_response = response.json()

        agent_message = AgentMessage(
            content=agent_response["choices"][0]["message"]["content"]
        )
        conversation.add_message(agent_message)
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        safe_prompt: bool = False,
    ) -> Conversation:
        """
        Make an asynchronous prediction using the Mistral API.

        Args:
            conversation (Conversation): The conversation object.
            toolkit (Optional): The toolkit for tool assistance.
            tool_choice (Optional): The tool choice strategy.
            temperature (float): The temperature for response variability.
            max_tokens (int): The maximum number of tokens for the response.
            safe_prompt (bool): Whether to use a safer prompt.

        Returns:
            Conversation: The updated conversation object.
        """
        formatted_messages = self._format_messages(conversation.history)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice,
            "safe_prompt": safe_prompt,
        }

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )

        payload["messages"] = messages

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        agent_response = response.json()
        agent_message = AgentMessage(
            content=agent_response["choices"][0]["message"]["content"]
        )
        conversation.add_message(agent_message)
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        safe_prompt: bool = False,
    ) -> Iterator[str]:
        """
        Stream a response from the Mistral API.

        This method sends a conversation and optional toolkit information to the Mistral API
        and returns a generator that yields response content as it is received.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            toolkit (Optional): The toolkit for tool assistance, providing external tools to be invoked.
            tool_choice (Optional): The tool choice strategy, such as "auto" or "manual".
            temperature (float): The sampling temperature for response variability.
            max_tokens (int): The maximum number of tokens to generate in the response.
            safe_prompt (bool): Whether to use a safer prompt, reducing potential harmful content.

        Yields:
            Iterator[str]: A streaming generator that yields the response content as text.

        Example:
            for response_text in model.stream(conversation):
                print(response_text)
        """
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice,
            "safe_prompt": safe_prompt,
        }

        response = self._client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )

        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        logging.info(f"messages: {messages}")

        response = self._client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        message_content = ""

        for line in response.iter_lines():
            json_str = line.replace("data: ", "")
            try:
                if json_str:
                    chunk = json.loads(json_str)
                    if chunk["choices"][0]["delta"]:
                        delta = chunk["choices"][0]["delta"]["content"]
                        message_content += delta
                        yield delta
            except json.JSONDecodeError:
                pass

        conversation.add_message(AgentMessage(content=message_content))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        safe_prompt: bool = False,
    ) -> AsyncIterator[str]:
        """
        Asynchronously stream a response from the Mistral API.

        This method sends a conversation and optional toolkit information to the Mistral API
        and returns an asynchronous generator that yields response content as it is received.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            toolkit (Optional): The toolkit for tool assistance, providing external tools to be invoked.
            tool_choice (Optional): The tool choice strategy, such as "auto" or "manual".
            temperature (float): The sampling temperature for response variability.
            max_tokens (int): The maximum number of tokens to generate in the response.
            safe_prompt (bool): Whether to use a safer prompt, reducing potential harmful content.

        Yields:
            AsyncIterator[str]: An asynchronous streaming generator that yields the response content as text.

        Example:
            async for response_text in model.astream(conversation):
                print(response_text)
        """
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice,
            "safe_prompt": safe_prompt,
        }

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )

        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        logging.info(f"messages: {messages}")

        response = await self._async_client.post(self._BASE_URL, json=payload)
        response.raise_for_status()

        message_content = ""

        async for line in response.aiter_lines():
            json_str = line.replace("data: ", "")
            try:
                if json_str:
                    chunk = json.loads(json_str)
                    if chunk["choices"][0]["delta"]:
                        delta = chunk["choices"][0]["delta"]["content"]
                        message_content += delta
                        yield delta
            except json.JSONDecodeError:
                pass

        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        safe_prompt: bool = False,
    ) -> List[Conversation]:
        """
        Synchronously processes multiple conversations and generates responses for each.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float, optional): Sampling temperature for response generation.
            max_tokens (int, optional): Maximum tokens for the response.
            top_p (int, optional): Nucleus sampling parameter.
            enable_json (bool, optional): If True, enables JSON output format.
            safe_prompt (bool, optional): If True, enables safe prompting.

        Returns:
            List[Conversation]: List of updated conversations with generated responses.
        """
        return [
            self.predict(
                conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                safe_prompt=safe_prompt,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        safe_prompt: bool = False,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Asynchronously processes multiple conversations with controlled concurrency.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float, optional): Sampling temperature for response generation.
            max_tokens (int, optional): Maximum tokens for the response.
            top_p (int, optional): Nucleus sampling parameter.
            enable_json (bool, optional): If True, enables JSON output format.
            safe_prompt (bool, optional): If True, enables safe prompting.
            max_concurrent (int, optional): Maximum number of concurrent tasks.

        Returns:
            List[Conversation]: List of updated conversations with generated responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    safe_prompt=safe_prompt,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
