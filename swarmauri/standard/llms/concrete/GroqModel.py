import json
from typing import List, Optional, Dict
from groq import Groq
from swarmauri.standard.models.base.LLMBase import LLMBase

class GroqModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "mixtral-8x7b-32768"

    def predict(self, messages: List[Dict], 
                temperature: float = 0.7, 
                max_tokens: int = 256, 
                top_p: float = 1.0, 
                enable_json: bool = False, 
                stop: Optional[List[str]] = None) -> str:

        client = Groq(api_key=self.api_key)
        stop = stop or []
        
        response_format = {"type": "json_object"} if enable_json else None
        response = client.chat.completions.create(
            model=self.name,
            messages=messages,
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