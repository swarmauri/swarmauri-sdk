import json
import logging
from typing import List, Literal, Dict, Any
from shuttleai import ShuttleAI 
from shuttleai import shuttle 
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.ShuttleAISchemaConverter import ShuttleAISchemaConverter

class ShuttleAIToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = [
        "shuttle-tools",
        "gemini-pro",
        "mixtral-8x7b",
        "mistral-7b",
        "gpt-3.5-turbo",
        "gpt-4-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-0125"
    ]
    name: str = "shuttle-2-turbo"
    type: Literal['ShuttleAIToolModel'] = 'ShuttleAIToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [ShuttleAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = ShuttleAI(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = shuttle.chat_completion(
            model=self.name, 
            messages=formatted_messages, 
            tools=self._schema_convert_tools(toolkit.tools), 
            tool_choice=tool_choice, 
            temperature=temperature, 
            max_tokens=max_tokens, 
        )

        logging.info(f"tool_response: {tool_response}")
        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0]['message']['tool_calls']
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call['function']['name'] 
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call['function']['arguments'])
                func_result = func_call(**func_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_result,
                    }
                )
        logging.info(f'messages: {messages}')
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation