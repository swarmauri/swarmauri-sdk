from dataclasses import dataclass
from groq import Groq
from swarmauri.standard.models.base.ModelBase import ModelBase

@dataclass
class GroqToolModel(ModelBase, IPredict):
    allowed_models = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    api_key: str = ""
    model_name: str = "mixtral-8x7b-32768"

    def __post_init__(self):
        self._validate_model_name()
        self.client = Groq(api_key=api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")
    
        

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