from openai import OpenAI
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict

class OpenAIToolModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo-0125"):
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)

    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, max_tokens=1024):
        if tools and not tool_choice:
            tool_choice = "auto"
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response