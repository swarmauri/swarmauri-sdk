import json
from openai import OpenAI
from ..base.ModelBase import ModelBase
from ....core.models.IPredict import IPredict

class OpenAIImageGenerator(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "dall-e"):
        """
        Initializes the OpenAI image generator model.

        Parameters:
        - api_key (str): The API key provided by OpenAI for access to their services.
        - model_name (str): Name of the image generation model provided by OpenAI.
                            Defaults to "dall-e" for DALL·E, their image generation model.
        """
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)

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