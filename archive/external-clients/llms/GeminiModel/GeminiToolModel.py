import asyncio
import logging
from typing import List, Literal, Dict, Any
from google.generativeai.protos import FunctionDeclaration
from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.GeminiSchemaConverter import (
    GeminiSchemaConverter,
)
import google.generativeai as genai

from swarmauri.toolkits.concrete.Toolkit import Toolkit


class GeminiToolModel(LLMBase):
    """
    3rd Party's Resources: https://ai.google.dev/api/python/google/generativeai/protos/
    """

    api_key: str
    allowed_models: List[str] = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        # "gemini-1.0-pro",  giving an unexpected response
    ]
    name: str = "gemini-1.5-pro"
    type: Literal["GeminiToolModel"] = "GeminiToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        response = [GeminiSchemaConverter().convert(tools[tool]) for tool in tools]
        logging.info(response)
        return self._format_tools(response)

    def _format_tools(
        self, tools: List[SubclassUnion[FunctionMessage]]
    ) -> List[Dict[str, Any]]:
        formatted_tool = []
        for tool in tools:
            for parameter in tool["parameters"]["properties"]:
                tool["parameters"]["properties"][parameter] = genai.protos.Schema(
                    **tool["parameters"]["properties"][parameter]
                )

            tool["parameters"] = genai.protos.Schema(**tool["parameters"])

            tool = FunctionDeclaration(**tool)
            formatted_tool.append(tool)

        return formatted_tool

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ["content", "role", "tool_call_id", "tool_calls"]
        sanitized_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "system"
        ]

        for message in sanitized_messages:
            if message["role"] == "assistant":
                message["role"] = "model"

            if message["role"] == "tool":
                message["role"] = "user"

            # update content naming
            message["parts"] = message.pop("content")

        return sanitized_messages

    def predict(self, conversation, toolkit=None, temperature=0.7, max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        safety_settings = [
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

        tool_config = {
            "function_calling_config": {"mode": "ANY"},
        }

        client = genai.GenerativeModel(
            model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            tool_config=tool_config,
        )

        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools)

        logging.info(f"formatted_messages: {formatted_messages}")
        logging.info(f"tools: {tools}")

        tool_response = client.generate_content(
            formatted_messages,
            tools=tools,
        )
        logging.info(f"tool_response: {tool_response}")

        formatted_messages.append(tool_response.candidates[0].content)

        logging.info(
            f"tool_response.candidates[0].content: {tool_response.candidates[0].content}"
        )

        tool_calls = tool_response.candidates[0].content.parts

        tool_results = {}
        for tool_call in tool_calls:
            func_name = tool_call.function_call.name
            func_args = tool_call.function_call.args
            logging.info(f"func_name: {func_name}")
            logging.info(f"func_args: {func_args}")

            func_call = toolkit.get_tool_by_name(func_name)
            func_result = func_call(**func_args)
            logging.info(f"func_result: {func_result}")
            tool_results[func_name] = func_result

        formatted_messages.append(
            genai.protos.Content(
                role="function",
                parts=[
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn,
                            response={
                                "result": val,  # Return the API response to Gemini
                            },
                        )
                    )
                    for fn, val in tool_results.items()
                ],
            )
        )

        logging.info(f"formatted_messages: {formatted_messages}")

        agent_response = client.generate_content(formatted_messages)

        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f"conversation: {conversation}")
        return conversation

    async def apredict(
        self, conversation, toolkit=None, temperature=0.7, max_tokens=256
    ):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.predict, conversation, toolkit, temperature, max_tokens
        )

    def stream(self, conversation, toolkit=None, temperature=0.7, max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
        }

        safety_settings = [
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

        tool_config = {
            "function_calling_config": {"mode": "ANY"},
        }

        client = genai.GenerativeModel(
            model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            tool_config=tool_config,
        )

        formatted_messages = self._format_messages(conversation.history)
        tools = self._schema_convert_tools(toolkit.tools)

        logging.info(f"formatted_messages: {formatted_messages}")
        logging.info(f"tools: {tools}")

        tool_response = client.generate_content(
            formatted_messages,
            tools=tools,
        )
        logging.info(f"tool_response: {tool_response}")

        formatted_messages.append(tool_response.candidates[0].content)

        logging.info(
            f"tool_response.candidates[0].content: {tool_response.candidates[0].content.parts}"
        )

        tool_calls = tool_response.candidates[0].content.parts

        tool_results = {}
        for tool_call in tool_calls:
            if tool_call.function_call.name == "call":
                func_name = (
                    tool_response.candidates[0].content.parts[0].function_call.args.tool
                )
            else:
                func_name = tool_call.function_call.name
            func_args = tool_call.function_call.args
            logging.info(f"func_name: {func_name}")
            logging.info(f"func_args: {func_args}")

            func_call = toolkit.get_tool_by_name(func_name)
            func_result = func_call(**func_args)
            logging.info(f"func_result: {func_result}")
            tool_results[func_name] = func_result

        formatted_messages.append(
            genai.protos.Content(
                role="function",
                parts=[
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn,
                            response={
                                "result": val,  # Return the API response to Gemini
                            },
                        )
                    )
                    for fn, val in tool_results.items()
                ],
            )
        )

        logging.info(f"formatted_messages: {formatted_messages}")

        stream_response = client.generate_content(formatted_messages, stream=True)

        full_response = ""
        for chunk in stream_response:
            chunk_text = chunk.text
            full_response += chunk_text
            yield chunk_text

        logging.info(f"agent_response: {full_response}")
        conversation.add_message(AgentMessage(content=full_response))

    async def astream(
        self, conversation, toolkit=None, temperature=0.7, max_tokens=256
    ):
        loop = asyncio.get_event_loop()
        stream_gen = self.stream(conversation, toolkit, temperature, max_tokens)

        def safe_next(gen):
            try:
                return next(gen), False
            except StopIteration:
                return None, True

        while True:
            try:
                chunk, done = await loop.run_in_executor(None, safe_next, stream_gen)
                if done:
                    break
                yield chunk
            except Exception as e:
                print(f"Error in astream: {e}")
                break

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                toolkit=toolkit,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        max_concurrent: int = 5,
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
