import httpx
from typing import List, Literal
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
import asyncio
import contextlib


class HyperbolicImgGenModel(ImageGenBase):
    """
    A model class for generating images from text prompts using Hyperbolic's image generation API.

    Attributes:
        api_key (str): The API key for authenticating with the Hyperbolic API.
        allowed_models (List[str]): A list of available models for image generation.
        asyncio (ClassVar): The asyncio module for handling asynchronous operations.
        name (str): The name of the model to be used for image generation.
        type (Literal["HyperbolicImgGenModel"]): The type identifier for the model class.
        height (int): Height of the generated image.
        width (int): Width of the generated image.
        steps (int): Number of inference steps.
        cfg_scale (float): Classifier-free guidance scale.
        enable_refiner (bool): Whether to enable the refiner model.
        backend (str): Computational backend for the model.

    Link to Allowed Models: https://app.hyperbolic.xyz/models
    Link to API KEYS: https://app.hyperbolic.xyz/settings
    """

    _BASE_URL: str = PrivateAttr("https://api.hyperbolic.xyz/v1/image/generation")
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)

    api_key: str
    allowed_models: List[str] = [
        "SDXL1.0-base",
        "SD1.5",
        "SSD",
        "SD2",
        "SDXL-turbo",
    ]

    name: str = "SDXL1.0-base"  # Default model
    type: Literal["HyperbolicImgGenModel"] = "HyperbolicImgGenModel"

    # Additional configuration parameters
    height: int = 1024
    width: int = 1024
    steps: int = 30
    cfg_scale: float = 5.0
    enable_refiner: bool = False
    backend: str = "auto"

    def __init__(self, **kwargs):
        """
        Initializes the HyperbolicImgGenModel instance.

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
        return {
            "model_name": self.name,
            "prompt": prompt,
            "height": self.height,
            "width": self.width,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "enable_refiner": self.enable_refiner,
            "backend": self.backend,
        }

    @retry_on_status_codes((429, 529), max_retries=1)
    def _send_request(self, prompt: str) -> dict:
        """
        Sends a synchronous request to the Hyperbolic API for image generation.

        Args:
            prompt (str): The text prompt used for generating the image.

        Returns:
            dict: The response data from the API.
        """
        payload = self._create_request_payload(prompt)
        response = self._client.post(self._BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_send_request(self, prompt: str) -> dict:
        """
        Sends an asynchronous request to the Hyperbolic API for image generation.

        Args:
            prompt (str): The text prompt used for generating the image.

        Returns:
            dict: The response data from the API.
        """
        client = await self._get_async_client()
        payload = self._create_request_payload(prompt)
        response = await client.post(self._BASE_URL, json=payload)
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
        return response_data["images"][0]["image"]

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
            return response_data["images"][0]["image"]
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
                    return response_data["images"][0]["image"]

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
