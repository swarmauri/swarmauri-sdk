import logging
import json
from typing import List, Literal
from typing import List, Dict, Any, Literal
import cohere
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.CohereSchemaConverter import CohereSchemaConverter

class CohereToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['command-light',
    'command', 
    'command-r',
    'command-r-plus']
    name: str = "command-light"
    type: Literal['CohereToolModel'] = 'CohereToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = cohere.Client(api_key=self.api_key)
        preamble = "" # 🚧  Placeholder for implementation logic

        logging.info(f"_schema_convert_tools: {self._schema_convert_tools(toolkit.tools)}")
        logging.info(f"message: {formatted_messages[-1]}")
        logging.info(f"formatted_messages: {formatted_messages}")

        tool_response = client.chat(
            model=self.name, 
            message=formatted_messages[-1]['content'], 
            chat_history=formatted_messages[:-1],
            tools=self._schema_convert_tools(toolkit.tools)
        )


        logging.info(f"tool_response: {tool_response}")
        while tool_response.tool_calls:
          logging.info(tool_response.text) 
          tool_results = []
          for call in tool_response.tool_calls:
            logging.info(f"call: {call}")
            tmp_results = {"call": call, "outputs": ""}
            tool_results.append(tmp_results)
            # use the `web_search` tool with the search query the model sent back
            # web_search_results = {"call": call, "outputs": web_search(call.parameters["query"])}
            # tool_results.append(web_search_results)
            ...

        agent_response = client.chat(
            model=self.name,
            message="",
            chat_history=tool_response.chat_history,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_results=tool_results
        )

        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f"conversation: {conversation}")
        return conversation
