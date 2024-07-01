import json
from typing import List, Literal
import google.generativeai as genai
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class GeminiToolModel(LLMBase):
    type: Literal['GeminiToolModel'] = 'GeminiToolModel'


    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        list_of_msg_dicts = [message.model_dump(include=message_properties) for message in messages]
        formatted_messages = [
            {key: value for key, value in m.items() if value is not None}
            for m in list_of_msg_dicts
        ]
        return formatted_messages