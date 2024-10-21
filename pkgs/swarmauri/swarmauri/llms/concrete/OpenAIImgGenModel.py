import json
from pydantic import Field
import asyncio
from typing import List, Dict, Literal, Optional
from openai import OpenAI, AsyncOpenAI
from swarmauri.llms.base.LLMBase import LLMBase


class OpenAIImgGenModel(LLMBase):
    """
    Provider resources: https://platform.openai.com/docs/api-reference/images
    """

    api_key: str
    allowed_models: List[str] = ["dall-e-2", "dall-e-3"]
    name: str = "dall-e-3"
    type: Literal["OpenAIImgGenModel"] = "OpenAIImgGenModel"
    client: OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[str]:
        """
        Generate images using the OpenAI DALL-E model.

        Parameters:
        - prompt (str): The prompt to generate images from.
        - size (str): Size of the generated images. Options: "256x256", "512x512", "1024x1024", "1024x1792", "1792x1024".
        - quality (str): Quality of the generated images. Options: "standard", "hd" (only for DALL-E 3).
        - n (int): Number of images to generate (max 10 for DALL-E 2, 1 for DALL-E 3).
        - style (str): Optional. The style of the generated images. Options: "vivid", "natural" (only for DALL-E 3).

        Returns:
        - List of URLs of the generated images.
        """
        if self.name == "dall-e-3" and n > 1:
            raise ValueError("DALL-E 3 only supports generating 1 image at a time.")

        kwargs = {
            "model": self.name,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
        }

        if style and self.name == "dall-e-3":
            kwargs["style"] = style

        response = self.client.images.generate(**kwargs)
        return [image.url for image in response.data]

    async def agenerate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[str]:
        """Asynchronous version of generate_image"""
        if self.name == "dall-e-3" and n > 1:
            raise ValueError("DALL-E 3 only supports generating 1 image at a time.")

        kwargs = {
            "model": self.name,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
        }

        if style and self.name == "dall-e-3":
            kwargs["style"] = style

        response = await self.async_client.images.generate(**kwargs)
        return [image.url for image in response.data]

    def batch(
        self,
        prompts: List[str],
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
    ) -> List[List[str]]:
        """Synchronously process multiple prompts"""
        return [
            self.generate_image(
                prompt,
                size=size,
                quality=quality,
                n=n,
                style=style,
            )
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
        """Process multiple prompts in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt):
            async with semaphore:
                return await self.agenerate_image(
                    prompt,
                    size=size,
                    quality=quality,
                    n=n,
                    style=style,
                )

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
