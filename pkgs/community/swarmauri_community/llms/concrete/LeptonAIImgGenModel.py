import os
import asyncio
import requests
from io import BytesIO
from PIL import Image
from typing import List, Literal, Optional, Union, Dict
from pydantic import Field, ConfigDict
from swarmauri.llms.base.LLMBase import LLMBase


class LeptonAIImgGenModel(LLMBase):
    """
    A model for generating images from text using Lepton AI's SDXL image generation model.
    It returns the image as bytes.
    Get your API KEY from Lepton AI.
    """

    api_key: str = Field(default_factory=lambda: os.environ.get("LEPTON_API_KEY"))
    model_name: str = Field(default="sdxl")
    type: Literal["LeptonAIImgGenModel"] = "LeptonAIImgGenModel"
    base_url: str = Field(default="https://sdxl.lepton.run")

    model_config = ConfigDict(protected_namespaces=())

    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key:
            os.environ["LEPTON_API_KEY"] = self.api_key

    def _send_request(self, prompt: str, **kwargs) -> bytes:
        """Send a request to Lepton AI's API for image generation."""
        client = requests.Session()
        client.headers.update({"Authorization": f"Bearer {self.api_key}"})

        payload = {
            "prompt": prompt,
            "height": kwargs.get("height", 1024),
            "width": kwargs.get("width", 1024),
            "guidance_scale": kwargs.get("guidance_scale", 5),
            "high_noise_frac": kwargs.get("high_noise_frac", 0.75),
            "seed": kwargs.get("seed", None),
            "steps": kwargs.get("steps", 30),
            "use_refiner": kwargs.get("use_refiner", False),
        }

        response = client.post(f"{self.base_url}/run", json=payload)
        response.raise_for_status()
        return response.content

    def generate_image(self, prompt: str, **kwargs) -> bytes:
        """Generates an image based on the prompt and returns the image as bytes."""
        return self._send_request(prompt, **kwargs)

    async def agenerate_image(self, prompt: str, **kwargs) -> bytes:
        """Asynchronously generates an image based on the prompt and returns the image as bytes."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_image, prompt, **kwargs)

    def batch(self, prompts: List[str], **kwargs) -> List[bytes]:
        """
        Generates images for a batch of prompts.
        Returns a list of image bytes.
        """
        image_bytes_list = []
        for prompt in prompts:
            image_bytes = self.generate_image(prompt=prompt, **kwargs)
            image_bytes_list.append(image_bytes)
        return image_bytes_list

    async def abatch(
        self, prompts: List[str], max_concurrent: int = 5, **kwargs
    ) -> List[bytes]:
        """
        Asynchronously generates images for a batch of prompts.
        Returns a list of image bytes.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt):
            async with semaphore:
                return await self.agenerate_image(prompt=prompt, **kwargs)

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)

    @staticmethod
    def save_image(image_bytes: bytes, filename: str):
        """Utility method to save the image bytes to a file."""
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print(f"Image saved as {filename}")

    @staticmethod
    def display_image(image_bytes: bytes):
        """Utility method to display the image using PIL."""
        image = Image.open(BytesIO(image_bytes))
        image.show()
