import requests
import base64
from typing import List, Literal
from pydantic import Field
from swarmauri.llms.base.LLMBase import LLMBase
import asyncio
from typing import ClassVar


class DeepInfraImgGenModel(LLMBase):
    """
    A model for generating images from text using DeepInfra's image generation models.
    Resource: https://deepinfra.com/models/text-to-image/
    """

    api_key: str
    allowed_models: List[str] = [
        "black-forest-labs/FLUX-1-dev",
        "black-forest-labs/FLUX-1-schnell",
        "stabilityai/sdxl-turbo",
        "stabilityai/stable-diffusion-2-1",
    ]

    asyncio: ClassVar = asyncio
    name: str = "stabilityai/stable-diffusion-2-1"  # Default model
    type: Literal["DeepInfraImgGenModel"] = "DeepInfraImgGenModel"

    def _send_request(self, prompt: str) -> dict:
        """Send a request to DeepInfra's API for image generation."""
        url = f"https://api.deepinfra.com/v1/inference/{self.name}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"prompt": prompt}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def generate_image_base64(self, prompt: str) -> str:
        """Generates an image based on the prompt and returns the base64-encoded string."""
        # Send request to DeepInfra API
        response_data = self._send_request(prompt)

        # Extract the base64 image (the part after the data type prefix)
        image_base64 = response_data["images"][0].split(",")[1]

        return image_base64

    async def agenerate_image_base64(self, prompt: str) -> str:
        """Asynchronously generates an image based on the prompt and returns the base64-encoded string."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_image_base64, prompt)

    def batch_base64(self, prompts: List[str]) -> List[str]:
        """
        Generates base64-encoded images for a batch of prompts.
        Returns a list of base64 strings.
        """
        base64_images = []
        for prompt in prompts:
            base64_images.append(self.generate_image_base64(prompt=prompt))

        return base64_images

    async def abatch_base64(
        self, prompts: List[str], max_concurrent: int = 5
    ) -> List[str]:
        """
        Asynchronously generates base64-encoded images for a batch of prompts.
        Returns a list of base64 strings.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt):
            async with semaphore:
                return await self.agenerate_image_base64(prompt=prompt)

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
