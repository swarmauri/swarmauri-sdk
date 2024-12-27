from pydantic import PrivateAttr
import asyncio
import httpx
from typing import Dict, List, Literal, Optional
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri.utils.retry_decorator import retry_on_status_codes


class OpenAIImgGenModel(ImageGenBase):
    """
    OpenAIImgGenModel is a class for generating images using OpenAI's DALL-E models.

    Attributes:
        api_key (str): The API key for authenticating with the OpenAI API.
        allowed_models (List[str]): List of allowed model names.
        name (str): The name of the model to use.
        type (Literal["OpenAIImgGenModel"]): The type of the model.

    Provider Resources: https://platform.openai.com/docs/api-reference/images/generate
    """

    api_key: str
    allowed_models: List[str] = ["dall-e-2", "dall-e-3"]
    name: str = "dall-e-3"
    type: Literal["OpenAIImgGenModel"] = "OpenAIImgGenModel"
    _BASE_URL: str = PrivateAttr(default="https://api.openai.com/v1/images/generations")
    _headers: Dict[str, str] = PrivateAttr(default=None)

    def __init__(self, **kwargs) -> None:
        """
        Initialize the GroqAIAudio class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**kwargs)
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry_on_status_codes((429, 529), max_retries=1)
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[str]:
        """
        Generate images using the OpenAI DALL-E model synchronously.

        Parameters:
        - prompt (str): The prompt to generate images from.
        - size (str): Size of the generated images.
        - quality (str): Quality of the generated images.
        - n (int): Number of images to generate.
        - style (str): Optional style of the generated images.

        Returns:
        - List of URLs of the generated images.
        """
        if self.name == "dall-e-3" and n > 1:
            raise ValueError("DALL-E 3 only supports generating 1 image at a time.")

        payload = {
            "model": self.name,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
        }

        if style and self.name == "dall-e-3":
            payload["style"] = style

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()
                return [image["url"] for image in response.json().get("data", [])]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Image generation failed: {e}")

    @retry_on_status_codes((429, 529), max_retries=1)
    async def agenerate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[str]:
        """
        Generate images using the OpenAI DALL-E model asynchronously.

        Parameters:
        - prompt (str): The prompt to generate images from.
        - size (str): Size of the generated images.
        - quality (str): Quality of the generated images.
        - n (int): Number of images to generate.
        - style (str): Optional style of the generated images.

        Returns:
        - List of URLs of the generated images.
        """
        if self.name == "dall-e-3" and n > 1:
            raise ValueError("DALL-E 3 only supports generating 1 image at a time.")

        payload = {
            "model": self.name,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
        }

        if style and self.name == "dall-e-3":
            payload["style"] = style

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()
                return [image["url"] for image in response.json().get("data", [])]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Image generation failed: {e}")

    def batch(
        self,
        prompts: List[str],
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[List[str]]:
        """
        Synchronously process multiple prompts for image generation.

        Parameters:
        - prompts (List[str]): List of prompts.
        - size (str): Size of the generated images.
        - quality (str): Quality of the generated images.
        - n (int): Number of images to generate.
        - style (str): Optional style of the generated images.

        Returns:
        - List of lists of URLs of the generated images.
        """
        return [
            self.generate_image(prompt, size=size, quality=quality, n=n, style=style)
            for prompt in prompts
        ]

    async def abatch(
        self,
        prompts: List[str],
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
        max_concurrent: int = 5,
    ) -> List[List[str]]:
        """
        Asynchronously process multiple prompts for image generation with controlled concurrency.

        Parameters:
        - prompts (List[str]): List of prompts.
        - size (str): Size of the generated images.
        - quality (str): Quality of the generated images.
        - n (int): Number of images to generate.
        - style (str): Optional style of the generated images.
        - max_concurrent (int): Maximum number of concurrent requests.

        Returns:
        - List of lists of URLs of the generated images.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt) -> List[str]:
            async with semaphore:
                return await self.agenerate_image(
                    prompt, size=size, quality=quality, n=n, style=style
                )

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
