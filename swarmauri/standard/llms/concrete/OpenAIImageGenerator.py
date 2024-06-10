import json
from dataclasses import dataclass
from openai import OpenAI
from swarmauri.core.models.base.ModelBase import ModelBase

@dataclass
class OpenAIImageGenerator(ModelBase):
    allowed_models = ['dall-e']
    api_key: str = ""
    model_name: str = "dall-e"

    def __post_init__(self):
        self._validate_model_name()
        self.client =  OpenAI(api_key=self.api_key)

    def _validate_model_name(self):
        if self.model_name not in self.allowed_models:
            raise ValueError(f"Invalid model name: {self.model_name}. Allowed models are: {self.allowed_models}")

    def predict(self, prompt: str, size: str = "1024x1024", 
                quality: str = "standard", n: int = 1) -> str:
        """
        Generates an image based on the given prompt and other parameters.

        Parameters:
        - prompt (str): A description of the image you want to generate.
        - **kwargs: Additional parameters that the image generation endpoint might use.

        Returns:
        - str: A URL or identifier for the generated image.
        """
        try:
            response = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            result = response.json()
            return result
        
        except Exception as e:
            return str(e)