from mistralai.client import MistralClient
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict

class MistralToolModel(ModelBase, IPredict):
    allowed_models = ['open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-large-latest',
    ]

    def __init__(self, api_key: str, model_name: str = 'open-mixtral-8x22b'):
        if model_name not in self.allowed_models:
            raise ValueError(f"Model name '{model_name}' is not supported. Choose from {self.allowed_models}")
        
        self.client = MistralClient(api_key=api_key)
        super().__init__(model_name)
        

    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, 
        max_tokens=1024, safe_prompt: bool = False):

        if tools and not tool_choice:
            tool_choice = "auto"
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            safe_prompt=safe_prompt
        )
        return response