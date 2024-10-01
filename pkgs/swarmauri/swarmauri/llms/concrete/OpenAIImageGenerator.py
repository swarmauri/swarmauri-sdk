import json
from typing import List, Literal
from openai import OpenAI
from swarmauri.llms.base.LLMBase import LLMBase


class OpenAIImageGenerator(LLMBase):
    """
    Provider resources: https://platform.openai.com/docs/guides/images/introduction
    """

    api_key: str
    allowed_models: List[str] = ["dall-e-3", "dall-e-2"]
    name: str = "dall-e-3"
    type: Literal["OpenAIImageGenerator"] = "OpenAIImageGenerator"

    def predict(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
    ) -> str:
        """
        Generates an image based on the given prompt and other parameters.

        Parameters:
        - prompt (str): A description of the image you want to generate.
        - **kwargs: Additional parameters that the image generation endpoint might use.

        Returns:
        - str: A URL or identifier for the generated image.
        """
        try:
            client = OpenAI(api_key=self.api_key)
            response = client.images.generate(
                model=self.name, prompt=prompt, size=size, quality=quality, n=n
            )
            result = response.json()
            return result

        except Exception as e:
            return str(e)
