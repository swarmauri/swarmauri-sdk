from typing import List
from openai import OpenAI
from swarmauri.standard.llms.base.LLMBase import LLMBase

class OpenAIToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613']
    name: str = "gpt-3.5-turbo-0125"

    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, max_tokens=1024):
        client = OpenAI(api_key=self.api_key)
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