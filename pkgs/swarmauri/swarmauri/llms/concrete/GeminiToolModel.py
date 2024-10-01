import logging
import json
from typing import List, Literal, Dict, Any
import google.generativeai as genai
from google.generativeai.protos import FunctionDeclaration
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.GeminiSchemaConverter import (
    GeminiSchemaConverter,
)
import google.generativeai as genai


class GeminiToolModel(LLMBase):
    """
    3rd Party's Resources: https://ai.google.dev/api/python/google/generativeai/protos/
    """

    api_key: str
    allowed_models: List[str] = ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
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
                message["role"] == "user"

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

        
        logging.info(f'formatted_messages: {formatted_messages}')
        logging.info(f'tools: {tools}')

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
