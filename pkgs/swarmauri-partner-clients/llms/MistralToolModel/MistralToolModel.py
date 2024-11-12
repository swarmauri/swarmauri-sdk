import asyncio
import json
import logging
from typing import AsyncIterator, Iterator, List, Literal, Dict, Any
import mistralai
from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.MistralSchemaConverter import (
    MistralSchemaConverter,
)


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
        client = mistralai.Mistral(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"
        tool_response = client.chat.complete(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt,
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)

                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        logging.info(f"messages: {messages}")

        agent_response = client.chat.complete(model=self.name, messages=messages)
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

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
        client = mistralai.Mistral(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = await client.chat.complete_async(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt,
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)

                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        logging.info(f"messages: {messages}")

        agent_response = await client.chat.complete_async(
            model=self.name, messages=messages
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

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

        Args:
            conversation (Conversation): The conversation object.
            toolkit (Optional): The toolkit for tool assistance.
            tool_choice (Optional): The tool choice strategy.
            temperature (float): The temperature for response variability.
            max_tokens (int): The maximum number of tokens for the response.
            safe_prompt (bool): Whether to use a safer prompt.

        Yields:
            Iterator[str]: The streaming response content.
        """
        client = mistralai.Mistral(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.complete(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt,
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)

                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        logging.info(f"messages: {messages}")

        stream_response = client.chat.stream(model=self.name, messages=messages)
        message_content = ""

        for chunk in stream_response:
            if hasattr(chunk, "data") and chunk.data.choices[0].delta.content:
                # Manually decode each line
                line = chunk.data.choices[0].delta.content.encode("utf-8").decode("utf-8")
                message_content += line
                yield line
    
        conversation.add_message(AgentMessage(content=message_content))

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

        Args:
            conversation (Conversation): The conversation object.
            toolkit (Optional): The toolkit for tool assistance.
            tool_choice (Optional): The tool choice strategy.
            temperature (float): The temperature for response variability.
            max_tokens (int): The maximum number of tokens for the response.
            safe_prompt (bool): Whether to use a safer prompt.

        Yields:
            AsyncIterator[str]: The streaming response content.
        """
        client = mistralai.Mistral(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = await client.chat.complete_async(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt,
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)

                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        logging.info(f"messages: {messages}")

        stream_response = await client.chat.stream_async(
            model=self.name, messages=messages
        )
        message_content = ""

        async for chunk in stream_response:
            await asyncio.sleep(0.2) # 🚧 this is not an ideal permanent fix
            if chunk.data.choices[0].delta.content:
                message_content += chunk.data.choices[0].delta.content
                yield chunk.data.choices[0].delta.content

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
