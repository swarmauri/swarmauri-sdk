import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type

import httpx
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.conversations.IConversation import IConversation

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.MistralSchemaConverter import (
    MistralSchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "MistralToolModel")
class MistralToolModel(ToolLLMBase):
    """
    A model class for interacting with the Mistral API for tool-assisted conversation and prediction.

    This class provides methods for synchronous and asynchronous communication with the Mistral API.
    It supports processing single and batch conversations, as well as streaming responses.

    Attributes:
        api_key (SecretStr): The API key for authenticating requests with the Mistral API.
        allowed_models (List[str]): A list of supported model names for the Mistral API.
        name (str): The default model name to use for predictions.
        type (Literal["MistralToolModel"]): The type identifier for the model.
        timeout (float): The timeout for API requests.

    Provider resources: https://docs.mistral.ai/capabilities/function_calling/#available-models
    """

    allowed_models: List[str] = [
        "mistral-medium-2508",
        "codestral-2508",
        "devstral-medium-2507",
        "mistral-ocr-2505",
        "ministral-8b-2410",
        "mistral-medium-2505",
        "codestral-2501",
        "mistral-large-2411",
        "pixtral-large-2411",
        "mistral-small-2407",
        "mistral-embed",
        "codestral-embed",
        "mistral-moderation-2411",
        "mistral-small-2506",
        "devstral-small-2507",
        "mistral-small-2501",
        "devstral-small-2505",
        "pixtral-12b-2409",
        "open-mistral-nemo",
    ]
    name: str = "mistral-medium-2508"
    type: Literal["MistralToolModel"] = "MistralToolModel"
    BASE_URL: str = "https://api.mistral.ai/v1/chat/completions"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)

    def __init__(self, **data: dict[str, Any]) -> None:
        """
        Initializes the MistralToolModel instance, setting up headers for API requests.

        Parameters:
            **data (dict[str, Any]): Arbitrary keyword arguments for initialization.
        """
        super().__init__(**data)
        self._headers = {"Authorization": f"Bearer {self.api_key.get_secret_value()}"}
        self._client = httpx.Client(
            headers=self._headers,
            timeout=self.timeout,
        )
        self._async_client = httpx.AsyncClient(
            headers=self._headers,
            timeout=self.timeout,
        )
        self.allowed_models = self.allowed_models or self.get_allowed_models()
        if not self.name and self.allowed_models:
            self.name = self.allowed_models[0]

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Returns the schema converter class for Mistral API.

        Returns:
            Type[SchemaConverterBase]: The MistralSchemaConverter class.
        """
        return MistralSchemaConverter

    def _schema_convert_tools(
        self, tools: Dict[str, SubclassUnion[ToolBase]]
    ) -> List[Dict[str, Any]]:
        """
        Convert a dictionary of tools to the schema format required by Mistral API.

        Args:
            tools (Dict[str, SubclassUnion[ToolBase]]): A dictionary of tool objects.

        Returns:
            List[Dict[str, Any]]: A list of converted tool schemas.
        """
        converter = self.get_schema_converter()()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history messages for the Mistral API.

        Args:
            messages (List[Type[MessageBase]]): List of message objects from the conversation history.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """
        message_properties = ["content", "role", "name", "tool_call_id"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "assistant" and message.role != "tool"
        ]
        return formatted_messages

    def _process_tool_calls(
        self, tool_calls: List[Any], toolkit: Toolkit, messages: List[Type[MessageBase]]
    ) -> List[Dict]:
        """
        Processes a list of tool calls and appends the results to the messages list.

        Args:
            tool_calls (list): Tool calls from the LLM response.
            toolkit (Toolkit): Toolkit containing tools to be called.
            messages (list): Message list to append tool responses to.

        Returns:
            List[Dict]: Updated list of messages with tool responses added.
        """
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
        return messages

    @retry_on_status_codes((429, 529), max_retries=1)
    def get_allowed_models(self) -> List[str]:
        """
        Get a list of allowed models for the Mistral API.

        Returns:
            List[str]: List of allowed model names.
        """
        try:
            response = self._client.get("https://api.mistral.ai/v1/models")
            response.raise_for_status()
            response_data = response.json()

            tool_models = [
                model["id"]
                for model in response_data["data"]
                if model.get("capabilities", {}).get("function_calling", False)
                and model.get("capabilities", {}).get("completion_chat", False)
            ]

            return tool_models
        except Exception as e:
            logging.warning(f"Error fetching models from Mistral API: {e}")
            # Return default models as fallback
            return ["mistral-medium", "mistral-large-latest"]

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        safe_prompt: bool = False,
    ) -> Conversation:
        """
        Make a synchronous prediction using the Mistral API.

        Args:
            conversation (Conversation): The conversation object.
            toolkit (Toolkit): The toolkit for tool assistance.
            tool_choice (dict): The tool choice strategy (default is "auto").
            multiturn (bool): Whether to follow up a tool call with another LLM request.
            temperature (float): The temperature for response variability.
            max_tokens (int): The maximum number of tokens for the response.
            safe_prompt (bool): Whether to use a safer prompt.

        Returns:
            IConversation: The updated conversation object.
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

        response = self._client.post(self.BASE_URL, json=payload)
        logging.info(f"Response: {response.json()}")
        response.raise_for_status()
        tool_response = response.json()

        if "choices" not in tool_response or not tool_response["choices"]:
            raise ValueError("Invalid response from Mistral API")

        messages = formatted_messages.copy()
        assistant_message = tool_response["choices"][0]["message"]
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Extract tool messages for the conversation
        tool_messages = [
            FunctionMessage(
                tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
            )
            for m in messages
            if m.get("role") == "tool"
        ]

        # Add tool messages to conversation
        conversation.add_messages(tool_messages)

        # For multiturn and if there were tool calls, make a follow-up request
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            response = self._client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            agent_response = response.json()

            if "choices" in agent_response and agent_response["choices"]:
                agent_message = AgentMessage(
                    content=agent_response["choices"][0]["message"]["content"]
                )
                conversation.add_message(agent_message)

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        safe_prompt: bool = False,
    ) -> Conversation:
        """
        Make an asynchronous prediction using the Mistral API.

        Args:
            conversation (Conversation): The conversation object.
            toolkit (Toolkit): The toolkit for tool assistance.
            tool_choice (dict): The tool choice strategy.
            multiturn (bool): Whether to follow up a tool call with another LLM request.
            temperature (float): The temperature for response variability.
            max_tokens (int): The maximum number of tokens for the response.
            safe_prompt (bool): Whether to use a safer prompt.

        Returns:
            IConversation: The updated conversation object.
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

        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as client:
            response = await client.post(self.BASE_URL, json=payload)
            logging.info(f"Response: {response.json()}")
            response.raise_for_status()
            tool_response = response.json()

        if "choices" not in tool_response or not tool_response["choices"]:
            raise ValueError("Invalid response from Mistral API")

        messages = formatted_messages.copy()
        assistant_message = tool_response["choices"][0]["message"]
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Extract tool messages for the conversation
        tool_messages = [
            FunctionMessage(
                tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
            )
            for m in messages
            if m.get("role") == "tool"
        ]

        # Add tool messages to conversation
        conversation.add_messages(tool_messages)

        # For multiturn and if there were tool calls, make a follow-up request
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            async with httpx.AsyncClient(
                headers=self._headers, timeout=self.timeout
            ) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                agent_response = response.json()

            if "choices" in agent_response and agent_response["choices"]:
                agent_message = AgentMessage(
                    content=agent_response["choices"][0]["message"]["content"]
                )
                conversation.add_message(agent_message)

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        safe_prompt: bool = False,
    ) -> Iterator[str]:
        """
        Stream a response from the Mistral API.

        This method sends a conversation and optional toolkit information to the Mistral API
        and returns a generator that yields response content as it is received.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            toolkit (Toolkit): The toolkit for tool assistance, providing external tools to be invoked.
            tool_choice (dict): The tool choice strategy, such as "auto" or "manual".
            temperature (float): The sampling temperature for response variability.
            max_tokens (int): The maximum number of tokens to generate in the response.
            safe_prompt (bool): Whether to use a safer prompt, reducing potential harmful content.

        Yields:
            Iterator[str]: A streaming generator that yields the response content as text.
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

        # First request to handle tool calls
        response = self._client.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        tool_response = response.json()

        if "choices" not in tool_response or not tool_response["choices"]:
            raise ValueError("Invalid response from Mistral API")

        messages = formatted_messages.copy()
        assistant_message = tool_response["choices"][0]["message"]
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Extract tool messages for the conversation
        tool_messages = [
            FunctionMessage(
                tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
            )
            for m in messages
            if m.get("role") == "tool"
        ]

        # Add tool messages to conversation
        conversation.add_messages(tool_messages)

        # Now make a streaming request for the final response
        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        response = self._client.post(self.BASE_URL, json=payload)
        response.raise_for_status()

        message_content = ""

        for line in response.iter_lines():
            # Convert bytes to string if needed
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line

            if not line_str or line_str == "data: [DONE]":
                continue

            if line_str.startswith("data: "):
                json_str = line_str.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if (
                            "choices" in chunk
                            and chunk["choices"]
                            and "delta" in chunk["choices"][0]
                            and "content" in chunk["choices"][0]["delta"]
                        ):
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                except json.JSONDecodeError:
                    pass

        # Add the final agent message to the conversation
        conversation.add_message(AgentMessage(content=message_content))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        safe_prompt: bool = False,
    ) -> AsyncIterator[str]:
        """
        Asynchronously stream a response from the Mistral API.

        This method sends a conversation and optional toolkit information to the Mistral API
        and returns an asynchronous generator that yields response content as it is received.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            toolkit (Toolkit): The toolkit for tool assistance, providing external tools to be invoked.
            tool_choice (dict): The tool choice strategy, such as "auto" or "manual".
            temperature (float): The sampling temperature for response variability.
            max_tokens (int): The maximum number of tokens to generate in the response.
            safe_prompt (bool): Whether to use a safer prompt, reducing potential harmful content.

        Yields:
            AsyncIterator[str]: An asynchronous streaming generator that yields the response content as text.
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

        # First request to handle tool calls
        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as client:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        if "choices" not in tool_response or not tool_response["choices"]:
            raise ValueError("Invalid response from Mistral API")

        messages = formatted_messages.copy()
        assistant_message = tool_response["choices"][0]["message"]
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Extract tool messages for the conversation
        tool_messages = [
            FunctionMessage(
                tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
            )
            for m in messages
            if m.get("role") == "tool"
        ]

        # Add tool messages to conversation
        conversation.add_messages(tool_messages)

        # Now make a streaming request for the final response
        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        message_content = ""

        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as client:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line or line == "data: [DONE]":
                    continue

                if line.startswith("data: "):
                    json_str = line.replace("data: ", "")
                    try:
                        if json_str:
                            chunk = json.loads(json_str)
                            if (
                                "choices" in chunk
                                and chunk["choices"]
                                and "delta" in chunk["choices"][0]
                                and "content" in chunk["choices"][0]["delta"]
                            ):
                                delta = chunk["choices"][0]["delta"]["content"]
                                message_content += delta
                                yield delta
                    except json.JSONDecodeError:
                        pass

        # Add the final agent message to the conversation
        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        safe_prompt: bool = False,
    ) -> List[Conversation]:
        """
        Synchronously processes multiple conversations and generates responses for each.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            toolkit (Toolkit): The toolkit for tool assistance.
            tool_choice (dict): The tool choice strategy.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum tokens for the response.
            safe_prompt (bool): If True, enables safe prompting.

        Returns:
            List[Conversation]: List of updated conversations with generated responses.
        """
        results = []
        for conv in conversations:
            result = self.predict(
                conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                safe_prompt=safe_prompt,
            )
            results.append(result)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        safe_prompt: bool = False,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Asynchronously processes multiple conversations with controlled concurrency.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            toolkit (Toolkit): The toolkit for tool assistance.
            tool_choice (dict): The tool choice strategy.
            temperature (float): Sampling temperature for response generation.
            max_tokens (int): Maximum tokens for the response.
            safe_prompt (bool): If True, enables safe prompting.
            max_concurrent (int): Maximum number of concurrent tasks.

        Returns:
            List[Conversation]: List of updated conversations with generated responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> IConversation:
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
