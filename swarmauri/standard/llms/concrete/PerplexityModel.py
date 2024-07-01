import json
from typing import List, Dict, Literal, Optional
import requests
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class PerplexityModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama-3-sonar-small-32k-chat',
        'llama-3-sonar-small-32k-online',
        'llama-3-sonar-large-32k-chat',
        'llama-3-sonar-large-32k-online',
        'llama-3-8b-instruct',
        'llama-3-70b-instruct',
        'mixtral-8x7b-instruct',
        'pplx-7b-online',
        'pplx-70b-online',
        'nemotron-4-340b-instruct',
        'gemma-2-9b-it',
        'gemma-2-27b-it']
    name: str = "pplx-7b-online"
    type: Literal['PerplexityModel'] = 'PerplexityModel'
    
    def _format_messages(self, messages: List[IMessage]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, messages: List[IMessage], 
        temperature=0.7, 
        max_tokens=256, 
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None
        ):


        if top_p and top_k:
            raise ValueError('Do not set top_p and top_k')


        formatted_messages = self._format_messages(messages)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": True,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)

        return(response.text)



