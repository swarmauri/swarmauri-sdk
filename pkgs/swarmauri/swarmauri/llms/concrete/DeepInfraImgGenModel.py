import requests
import base64
from io import BytesIO
from PIL import Image
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

    def generate_image(self, prompt: str, save_path: str = "generated_image.png"):
        """Generates an image based on the prompt and saves it to the specified path."""
        # Send request to DeepInfra API
        response_data = self._send_request(prompt)

        # Extract and decode the base64 image
        image_base64 = response_data["images"][0].split(",")[1]

        image_data = base64.b64decode(image_base64)

        # Create image from the decoded data
        image = Image.open(BytesIO(image_data))

        # Save the image to the file system
        image.save(save_path)
        print(f"Image saved to {save_path}")

    async def agenerate_image(
        self, prompt: str, save_path: str = "generated_image.png"
    ):
        """Asynchronously generates an image based on the prompt."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.generate_image, prompt, save_path)

    def batch(self, prompts: List[str], save_paths: List[str] = None) -> List[str]:
        """
        Generates images for a batch of prompts and saves them to specified paths.
        Returns a list of saved image paths.
        """
        if save_paths is None:
            save_paths = [f"generated_image_{i}.png" for i in range(len(prompts))]

        saved_paths = []
        for prompt, save_path in zip(prompts, save_paths):
            self.generate_image(prompt=prompt, save_path=save_path)
            saved_paths.append(save_path)

        return saved_paths

    import asyncio

    async def abatch(
        self, prompts: List[str], save_paths: List[str] = None, max_concurrent: int = 5
    ) -> List[str]:
        """
        Asynchronously generates images for a batch of prompts and saves them to specified paths.
        Returns a list of saved image paths.
        """
        if save_paths is None:
            save_paths = [f"generated_image_{i}.png" for i in range(len(prompts))]

        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt, save_path):
            async with semaphore:
                await self.agenerate_image(prompt=prompt, save_path=save_path)

        tasks = [
            process_prompt(prompt, save_path)
            for prompt, save_path in zip(prompts, save_paths)
        ]
        await asyncio.gather(*tasks)

        return save_paths
