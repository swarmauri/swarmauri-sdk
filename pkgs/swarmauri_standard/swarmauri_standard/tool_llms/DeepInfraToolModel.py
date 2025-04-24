import asyncio
import json
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Type,
    Union,
)

import httpx
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.conversations.IConversation import IConversation

from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "DeepInfraToolModel")
class DeepInfraToolModel(ToolLLMBase):
    """
    DeepInfraToolModel provides an interface to interact with DeepInfra's LLM service
    using the OpenAI-compatible API for tool usage.

    This class supports synchronous and asynchronous predictions, streaming of responses,
    and batch processing. It communicates with the DeepInfra API to manage conversations,
    format messages, and handle tool-related functions.

    Attributes:
        api_key (SecretStr): API key to authenticate with DeepInfra API.
        allowed_models (List[str]): List of permissible model names.
        name (str): Default model name for predictions.
        type (Literal): Type identifier for the model.
        timeout (float): Maximum time to wait for API responses.

    Provider information: https://deepinfra.com/docs/api/openai_api
    """

    name: str = ""
    type: Literal["DeepInfraToolModel"] = "DeepInfraToolModel"
    BASE_URL: str = "https://api.deepinfra.com/v1/openai/chat/completions"

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Initialize the DeepInfraToolModel with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        self.allowed_models = self.allowed_models or self.get_allowed_models()
        # Set default model if name is not provided
        if not self.name and self.allowed_models:
            self.name = self.allowed_models[0]

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Returns the schema converter class for DeepInfra API.

        Returns:
            Type[SchemaConverterBase]: The OpenAISchemaConverter class.
        """
        return OpenAISchemaConverter

    def _schema_convert_tools(self, tools: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Converts a toolkit's tools to the DeepInfra-compatible schema format.

        Args:
            tools (Dict[str, Any]): A dictionary of tools to be converted.

        Returns:
            List[Dict[str, Any]]: A list of tool schemas in OpenAI format.
        """
        converter = self.get_schema_converter()()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[MessageBase]) -> List[Dict[str, str]]:
        """
        Formats a list of messages to a schema that matches the DeepInfra API's expectations.

        Args:
            messages (List[MessageBase]): The conversation history.

        Returns:
            List[Dict[str, str]]: A formatted list of message dictionaries.
        """
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        return [
            m.model_dump(include=message_properties, exclude_none=True)
            for m in messages
            if m.role != "tool"
        ]

    def _process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        toolkit: Toolkit,
        messages: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Processes a list of tool calls and appends the results to the messages list.

        Args:
            tool_calls (List[Dict[str, Any]]): Tool calls from the LLM response.
            toolkit (Toolkit): Toolkit containing tools to be called.
            messages (List[Dict[str, Any]]): Message list to append tool responses to.

        Returns:
            List[Dict[str, Any]]: Updated list of messages with tool responses added.
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
    def predict(
        self,
        conversation: IConversation,
        toolkit: Optional[Toolkit] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Makes a synchronous prediction using the DeepInfra model.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
            toolkit (Optional[Toolkit]): Optional toolkit for tool conversion.
            tool_choice (Optional[Union[str, Dict[str, Any]]]): Tool selection strategy.
            multiturn (bool): Whether to follow up a tool call with additional LLM call.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            IConversation: Updated conversation with agent responses and tool calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()

        # Add the assistant message
        if "choices" in tool_response and tool_response["choices"]:
            assistant_message = tool_response["choices"][0]["message"]
            messages.append(assistant_message)

            # Process tool calls if any
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

        # For multiturn, make a follow-up request with the tool results
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.BASE_URL, headers=self._headers, json=payload
                )
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
        conversation: IConversation,
        toolkit: Optional[Toolkit] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Makes an asynchronous prediction using the DeepInfra model.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
            toolkit (Optional[Toolkit]): Optional toolkit for tool conversion.
            tool_choice (Optional[Union[str, Dict[str, Any]]]): Tool selection strategy.
            multiturn (bool): Whether to follow up a tool call with additional LLM call.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            IConversation: Updated conversation with agent responses and tool calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()

        # Add the assistant message
        if "choices" in tool_response and tool_response["choices"]:
            assistant_message = tool_response["choices"][0]["message"]
            messages.append(assistant_message)

            # Process tool calls if any
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

        # For multiturn, make a follow-up request with the tool results
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.BASE_URL, headers=self._headers, json=payload
                )
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
        conversation: IConversation,
        toolkit: Optional[Toolkit] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """
        Streams response from DeepInfra model in real-time.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
            toolkit (Optional[Toolkit]): Optional toolkit for tool conversion.
            tool_choice (Optional[Union[str, Dict[str, Any]]]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            Iterator[str]: Streamed response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        # First, make a non-streaming request to handle tool calls
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()

        # Process tool calls if any
        if "choices" in tool_response and tool_response["choices"]:
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

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
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
        conversation: IConversation,
        toolkit: Optional[Toolkit] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response from DeepInfra model.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
            toolkit (Optional[Toolkit]): Optional toolkit for tool conversion.
            tool_choice (Optional[Union[str, Dict[str, Any]]]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            AsyncIterator[str]: Streamed response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        # First, make a non-streaming request to handle tool calls
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()

        # Process tool calls if any
        if "choices" in tool_response and tool_response["choices"]:
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

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            agent_response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            agent_response.raise_for_status()

        message_content = ""
        async for line in agent_response.aiter_lines():
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
        conversations: List[IConversation],
        toolkit: Optional[Toolkit] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> List[IConversation]:
        """
        Processes a batch of conversations sequentially.

        Args:
            conversations (List[IConversation]): List of conversations to process.
            toolkit (Optional[Toolkit]): Optional toolkit for tool conversion.
            tool_choice (Optional[Union[str, Dict[str, Any]]]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            List[IConversation]: List of updated conversations with responses.
        """
        results = []
        for conv in conversations:
            result = self.predict(
                conversation=conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            results.append(result)
        return results

    async def abatch(
        self,
        conversations: List[IConversation],
        toolkit: Optional[Toolkit] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_concurrent: int = 5,
    ) -> List[IConversation]:
        """
        Processes a batch of conversations concurrently with limited concurrency.

        Args:
            conversations (List[IConversation]): List of conversations to process.
            toolkit (Optional[Toolkit]): Optional toolkit for tool conversion.
            tool_choice (Optional[Union[str, Dict[str, Any]]]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[IConversation]: List of updated conversations with responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: IConversation) -> IConversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)

    def get_allowed_models(self) -> List[str]:
        """
        Queries the LLMProvider API endpoint to retrieve the list of allowed models.

        Returns:
            List[str]: List of allowed model names.
        """
        models_data = [
            "meta-llama/Meta-Llama-3-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "mistralai/Mistral-7B-Instruct-v0.3",
        ]
        return models_data
