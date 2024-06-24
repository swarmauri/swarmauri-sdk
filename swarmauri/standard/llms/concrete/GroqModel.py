import json
from typing import List, Optional, Dict, Literal
from groq import Groq
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class GroqModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "mixtral-8x7b-32768"
    type: Literal['GroqModel'] = 'GroqModel'

    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        list_of_msg_dicts = [message.dict(include=message_properties, exclude_none=True) for message in messages]
        sanitized_messages = [
            {key: value for key, value in m.items() if value is not None}
            for m in list_of_msg_dicts
        ]
        return sanitized_messages

    def predict(self, messages: List[IMessage], 
                temperature: float = 0.7, 
                max_tokens: int = 256, 
                top_p: float = 1.0, 
                enable_json: bool = False, 
                stop: Optional[List[str]] = None) -> str:

        formatted_messages = self._format_messages(messages)

        client = Groq(api_key=self.api_key)
        stop = stop or []
        
        response_format = {"type": "json_object"} if enable_json else None
        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop
        )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content