import json
from typing import List
import cohere
from swarmauri.standard.models.base.LLMBase import LLMBase

class CohereModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['command-light',
    'command', 
    'command-r',
    'command-r-plus']
    name: str = "command-light"

    
    def predict(self, messages, temperature=0.7, max_tokens=256):
        client = cohere.Client(api_key=self.api_key)
        response = client.chat(
            model=self.name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_truncation='OFF',
            connectors=[]
        )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content