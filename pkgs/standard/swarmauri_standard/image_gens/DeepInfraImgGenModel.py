import httpx
from typing import List, Literal
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
import asyncio
import contextlib


class DeepInfraImgGenModel(ImageGenBase):
    """
    A model class for generating images from text prompts using DeepInfra's image generation API.

    Attributes:
        api_key (str): The API key for authenticating with the DeepInfra API.
        allowed_models (List[str]): A list of available models for image generation.
        asyncio (ClassVar): The asyncio module for handling asynchronous operations.
        name (str): The name of the model to be used for image generation.
        type (Literal["DeepInfraImgGenModel"]): The type identifier for the model class.

    Link to Allowed Models: https://deepinfra.com/models/text-to-image/
    Link to API KEY: https://deepinfra.com/dash/api_keys
    """

    _BASE_URL: str = PrivateAttr("https://api.deepinfra.com/v1/inference")
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)

    api_key: str
    allowed_models: List[str] = [
        "black-forest-labs/FLUX-1-dev",
        "black-forest-labs/FLUX-1-schnell",
        "stabilityai/sdxl-turbo",
        "stabilityai/stable-diffusion-2-1",
    ]

    name: str = "stabilityai/stable-diffusion-2-1"  # Default model
    type: Literal["DeepInfraImgGenModel"] = "DeepInfraImgGenModel"

    def __init__(self, **kwargs):
        """
        Initializes the DeepInfraImgGenModel instance.

        This constructor sets up HTTP clients for both synchronous and asynchronous
        operations and configures request headers with the provided API key.

        Args:
            **data: Keyword arguments for model initialization.
        """
        super().__init__(**kwargs)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self._client = httpx.Client(headers=self._headers, timeout=30)

    async def _get_async_client(self) -> httpx.AsyncClient:
        """
        Gets or creates an async client instance.
        """
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(headers=self._headers, timeout=30)
        return self._async_client

    async def _close_async_client(self):
        """
        Closes the async client if it exists and is open.
        """
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None

    def _create_request_payload(self, prompt: str) -> dict:
        """
        Creates the payload for the image generation request.
        """
        return {"prompt": prompt}

    @retry_on_status_codes((429, 529), max_retries=1)
    def _send_request(self, prompt: str) -> dict:
        """
        Sends a synchronous request to the DeepInfra API for image generation.

        Args:
            prompt (str): The text prompt used for generating the image.

        Returns:
            dict: The response data from the API.
        """

        url = f"{self._BASE_URL}/{self.name}"
        payload = self._create_request_payload(prompt)

        response = self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_send_request(self, prompt: str) -> dict:
        """
        Sends an asynchronous request to the DeepInfra API for image generation.

        Args:
            prompt (str): The text prompt used for generating the image.

        Returns:
            dict: The response data from the API.
        """

        client = await self._get_async_client()
        url = f"{self._BASE_URL}/{self.name}"
        payload = self._create_request_payload(prompt)

        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def generate_image_base64(self, prompt: str) -> str:
        """
        Generates an image synchronously based on the provided prompt and returns it as a base64-encoded string.

        Args:
            prompt (str): The text prompt used for generating the image.

        Returns:
            str: The base64-encoded representation of the generated image.
        """
        response_data = self._send_request(prompt)
        image_base64 = response_data["images"][0].split(",")[1]
        return image_base64

    async def agenerate_image_base64(self, prompt: str) -> str:
        """
        Generates an image asynchronously based on the provided prompt and returns it as a base64-encoded string.

        Args:
            prompt (str): The text prompt used for generating the image.

        Returns:
            str: The base64-encoded representation of the generated image.
        """
        try:
            response_data = await self._async_send_request(prompt)
            image_base64 = response_data["images"][0].split(",")[1]
            return image_base64
        finally:
            await self._close_async_client()

    def batch_base64(self, prompts: List[str]) -> List[str]:
        """
        Generates images for a batch of prompts synchronously and returns them as a list of base64-encoded strings.

        Args:
            prompts (List[str]): A list of text prompts for image generation.

        Returns:
            List[str]: A list of base64-encoded representations of the generated images.
        """
        return [self.generate_image_base64(prompt) for prompt in prompts]

    async def abatch_base64(
        self, prompts: List[str], max_concurrent: int = 5
    ) -> List[str]:
        """
        Generates images for a batch of prompts asynchronously and returns them as a list of base64-encoded strings.

        Args:
            prompts (List[str]): A list of text prompts for image generation.
            max_concurrent (int): The maximum number of concurrent tasks.

        Returns:
            List[str]: A list of base64-encoded representations of the generated images.
        """

        try:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_prompt(prompt):
                async with semaphore:
                    response_data = await self._async_send_request(prompt)
                    return response_data["images"][0].split(",")[1]

            tasks = [process_prompt(prompt) for prompt in prompts]
            return await asyncio.gather(*tasks)
        finally:
            await self._close_async_client()

    def __del__(self):
        """
        Cleanup method to ensure clients are closed.
        """
        self._client.close()
        if self._async_client is not None and not self._async_client.is_closed:
            with contextlib.suppress(Exception):
                asyncio.run(self._close_async_client())
