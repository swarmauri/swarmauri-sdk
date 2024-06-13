from typing import List
from groq import Groq
from swarmauri.standard.models.base.LLMBase import LLMBase

class GroqToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "mixtral-8x7b-32768"


    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, max_tokens=1024):
        client = Groq(api_key=self.api_key)
        if tools and not tool_choice:
            tool_choice = "auto"
        response = client.chat.completions.create(
            model=self.name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response