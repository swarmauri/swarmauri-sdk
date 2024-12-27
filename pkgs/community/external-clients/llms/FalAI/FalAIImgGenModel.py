import os
import fal_client
import asyncio
import requests
from io import BytesIO
from PIL import Image
from typing import List, Literal, Optional, Union, Dict
from pydantic import Field, ConfigDict
from swarmauri.llms.base.LLMBase import LLMBase


class FalAIImgGenModel(LLMBase):
    """
    A model for generating images from text using FluxPro's image generation model provided by FalAI.
    This model returns a URL to the generated image based on a provided text prompt.

    Attributes:
        allowed_models (List[str]): List of allowed model names for image generation.
        api_key (str): The API key for authenticating with FalAI services.
        model_name (str): The model name to use for generating images.
        type (Literal): The type identifier for the model.
        model_config (ConfigDict): Configuration dictionary with protected namespaces.

    Link to API KEY: https://fal.ai/dashboard/keys
    Link to Allowed Models: https://fal.ai/models?categories=text-to-image
    """

    allowed_models: List[str] = [
        "fal-ai/flux-pro",
        "fal-ai/flux-pro/new",
        "fal-ai/flux-pro/v1.1",
    ]
    api_key: str = Field(default_factory=lambda: os.environ.get("FAL_KEY"))
    model_name: str = Field(default="fal-ai/flux-pro")
    type: Literal["FalAIImgGenModel"] = "FalAIImgGenModel"

    model_config = ConfigDict(protected_namespaces=())

    def __init__(self, **data):
        """
        Initialize the FalAIImgGenModel with the API key, model name, and validation of the model name.

        Args:
            **data: Additional keyword arguments passed to initialize the model.

        Raises:
            ValueError: If the provided model_name is not in allowed_models.
        """
        super().__init__(**data)
        if self.api_key:
            os.environ["FAL_KEY"] = self.api_key
        if self.model_name not in self.allowed_models:
            raise ValueError(
                f"Invalid model name. Allowed models are: {', '.join(self.allowed_models)}"
            )

    def _send_request(self, prompt: str, **kwargs) -> Dict:
        """
        Send a request to the FluxPro API for generating an image from a text prompt.

        Args:
            prompt (str): The text prompt for generating the image.
            **kwargs: Additional arguments for the API request, such as style or aspect ratio.

        Returns:
            Dict: The API response containing details about the generated image, including its URL.
        """
        arguments = {"prompt": prompt, **kwargs}
        result = fal_client.subscribe(
            self.model_name,
            arguments=arguments,
            with_logs=True,
        )
        return result

    def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Generates an image based on the prompt and returns the image URL.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs: Additional parameters for the request.

        Returns:
            str: The URL of the generated image.
        """
        response_data = self._send_request(prompt, **kwargs)
        image_url = response_data["images"][0]["url"]
        return image_url

    async def agenerate_image(self, prompt: str, **kwargs) -> str:
        """
        Asynchronously generates an image based on the prompt and returns the image URL.

        Args:
            prompt (str): The text prompt for image generation
            **kwargs: Additional parameters to pass to the API

        Returns:
            str: The URL of the generated image
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_image, prompt, **kwargs)

    def batch(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Generates images for a batch of prompts.

        Args:
            prompts (List[str]): List of text prompts
            **kwargs: Additional parameters to pass to the API

        Returns:
            List[str]: List of image URLs
        """
        image_urls = []
        for prompt in prompts:
            image_url = self.generate_image(prompt=prompt, **kwargs)
            image_urls.append(image_url)
        return image_urls

    async def abatch(
        self, prompts: List[str], max_concurrent: int = 5, **kwargs
    ) -> List[str]:
        """
        Asynchronously generates images for a batch of prompts.

        Args:
            prompts (List[str]): List of text prompts
            max_concurrent (int): Maximum number of concurrent requests
            **kwargs: Additional parameters to pass to the API

        Returns:
            List[str]: List of image URLs
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt):
            async with semaphore:
                return await self.agenerate_image(prompt=prompt, **kwargs)

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
