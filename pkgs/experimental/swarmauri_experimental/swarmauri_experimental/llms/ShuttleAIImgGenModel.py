import os
import asyncio
import requests
from typing import List, Literal, Optional, Dict
from pydantic import Field, ConfigDict
from swarmauri.llms.base.LLMBase import LLMBase


class ShuttleAIImgGenModel(LLMBase):
    """
    A model for generating images using Shuttle AI's image generation API.
    It returns the URL to the generated image.
    Get your API key from: https://shuttleai.com/keys
    """

    allowed_models: List[str] = [
        "shuttleai/shuttle-2-diffusion",
        "openai/dall-e-3",
        "black-forest-labs/flux1-pro",
        "black-forest-labs/flux1-dev",
        "black-forest-labs/flux1-schnell",
        "stabilityai/sdxl",
        "stabilityai/sdxl-inpaint",
        "stabilityai/dreamshaperxl-v10",
        "stabilityai/juggernautxl",
        "stabilityai/turbovisionxl",
        "stabilityai/realistic-vision-v5.1",
    ]

    api_key: str = Field(default_factory=lambda: os.environ.get("SHUTTLE_API_KEY"))
    base_url: str = Field(default="https://api.shuttleai.app/v1")
    model_name: str = Field(default="shuttleai/shuttle-2-diffusion")
    type: Literal["ShuttleAIImgGenModel"] = "ShuttleAIImgGenModel"

    model_config = ConfigDict(protected_namespaces=())

    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key:
            os.environ["SHUTTLE_API_KEY"] = self.api_key
        if self.model_name not in self.allowed_models:
            raise ValueError(
                f"Invalid model name. Allowed models are: {', '.join(self.allowed_models)}"
            )
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _send_request(self, prompt: str, model: str, **kwargs) -> Dict:
        """Send a request to Shuttle AI's API for image generation."""
        if model not in self.allowed_models:
            raise ValueError(
                f"Invalid model name. Allowed models are: {', '.join(self.allowed_models)}"
            )

        url = f"{self.base_url}/images/generations"
        payload = {"model": model, "prompt": prompt, **kwargs}

        response = requests.post(url, json=payload, headers=self._headers)
        if response.status_code != 200:
            raise Exception(
                f"API request failed with status {response.status_code}: {response.text}"
            )

        return response.json()

    def generate_image(self, prompt: str, model: str = None, **kwargs) -> str:
        """Generates an image based on the prompt and returns the image URL."""
        model = model or self.model_name
        response_data = self._send_request(prompt=prompt, model=model, **kwargs)
        return response_data["data"][0]["url"]

    async def agenerate_image(self, prompt: str, model: str = None, **kwargs) -> str:
        """Asynchronously generates an image based on the prompt and returns the image URL."""
        model = model or self.model_name
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.generate_image, prompt, model, kwargs
        )

    def batch(self, prompts: List[str], model: str = None, **kwargs) -> List[str]:
        """
        Generates images for a batch of prompts.
        Returns a list of image URLs.
        """
        model = model or self.model_name
        image_urls = []
        for prompt in prompts:
            image_url = self.generate_image(prompt=prompt, model=model, **kwargs)
            image_urls.append(image_url)
        return image_urls

    async def abatch(
        self, prompts: List[str], model: str = None, max_concurrent: int = 5, **kwargs
    ) -> List[str]:
        """
        Asynchronously generates images for a batch of prompts.
        Returns a list of image URLs.
        """
        model = model or self.model_name
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt):
            async with semaphore:
                return await self.agenerate_image(prompt=prompt, model=model, **kwargs)

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
