import httpx
import time
from typing import List, Literal, Optional, Dict
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
import asyncio
import contextlib


class BlackForestImgGenModel(ImageGenBase):
    """
    A model for generating images using FluxPro's image generation models through the Black Forest API.
    Link to API key: https://api.bfl.ml/auth/profile
    """

    _BASE_URL: str = PrivateAttr("https://api.bfl.ml")
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _headers: Dict[str, str] = PrivateAttr(default=None)

    api_key: str
    allowed_models: List[str] = ["flux-pro-1.1", "flux-pro", "flux-dev"]

    name: str = "flux-pro"  # Default model
    type: Literal["BlackForestImgGenModel"] = "BlackForestImgGenModel"

    def __init__(self, **kwargs):
        """
        Initializes the BlackForestImgGenModel instance with HTTP clients.
        """
        super().__init__(**kwargs)
        self._headers = {
            "Content-Type": "application/json",
            "X-Key": self.api_key,
        }
        self._client = httpx.Client(headers=self._headers, timeout=30)

    async def _get_async_client(self) -> httpx.AsyncClient:
        """Gets or creates an async client instance."""
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(headers=self._headers, timeout=30)
        return self._async_client

    async def _close_async_client(self):
        """Closes the async client if it exists and is open."""
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None

    @retry_on_status_codes((429, 529), max_retries=1)
    def _send_request(self, endpoint: str, data: dict) -> dict:
        """Send a synchronous request to FluxPro's API for image generation."""
        url = f"{self._BASE_URL}/{endpoint}"
        response = self._client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_send_request(self, endpoint: str, data: dict) -> dict:
        """Send an asynchronous request to FluxPro's API for image generation."""
        client = await self._get_async_client()
        url = f"{self._BASE_URL}/{endpoint}"
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    def _get_result(self, task_id: str) -> dict:
        """Get the result of a generation task synchronously."""
        url = f"{self._BASE_URL}/v1/get_result"
        params = {"id": task_id}
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_get_result(self, task_id: str) -> dict:
        """Get the result of a generation task asynchronously."""
        client = await self._get_async_client()
        url = f"{self._BASE_URL}/v1/get_result"
        params = {"id": task_id}
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        steps: Optional[int] = None,
        prompt_upsampling: bool = False,
        seed: Optional[int] = None,
        guidance: Optional[float] = None,
        safety_tolerance: Optional[int] = None,
        interval: Optional[float] = None,
        max_wait_time: int = 300,
        check_interval: int = 10,
    ) -> Dict:
        """
        Generates an image based on the prompt and waits for the result synchronously.

        Args:
            prompt (str): The text prompt for image generation
            width (int): Image width in pixels
            height (int): Image height in pixels
            steps (Optional[int]): Number of inference steps
            prompt_upsampling (bool): Whether to use prompt upsampling
            seed (Optional[int]): Random seed for generation
            guidance (Optional[float]): Guidance scale
            safety_tolerance (Optional[int]): Safety tolerance level
            interval (Optional[float]): Interval parameter (flux-pro only)
            max_wait_time (int): Maximum time to wait for result in seconds
            check_interval (int): Time between status checks in seconds

        Returns:
            Dict: Dictionary containing the image URL and other result information
        """
        endpoint = f"v1/{self.name}"
        data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "prompt_upsampling": prompt_upsampling,
        }

        if steps is not None:
            data["steps"] = steps
        if seed is not None:
            data["seed"] = seed
        if guidance is not None:
            data["guidance"] = guidance
        if safety_tolerance is not None:
            data["safety_tolerance"] = safety_tolerance
        if interval is not None and self.name == "flux-pro":
            data["interval"] = interval

        response = self._send_request(endpoint, data)
        task_id = response["id"]

        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            result = self._get_result(task_id)
            if result["status"] == "Ready":
                return result["result"]["sample"]
            elif result["status"] in [
                "Error",
                "Request Moderated",
                "Content Moderated",
            ]:
                raise Exception(f"Task failed with status: {result['status']}")
            time.sleep(check_interval)

        raise TimeoutError(f"Image generation timed out after {max_wait_time} seconds")

    async def agenerate_image(self, prompt: str, **kwargs) -> Dict:
        """
        Asynchronously generates an image based on the prompt and waits for the result.

        Args:
            prompt (str): The text prompt for image generation
            **kwargs: Additional arguments passed to generate_image

        Returns:
            Dict: Dictionary containing the image URL and other result information
        """
        try:
            endpoint = f"v1/{self.name}"
            data = {
                "prompt": prompt,
                "width": kwargs.get("width", 1024),
                "height": kwargs.get("height", 768),
                "prompt_upsampling": kwargs.get("prompt_upsampling", False),
            }

            optional_params = [
                "steps",
                "seed",
                "guidance",
                "safety_tolerance",
            ]
            for param in optional_params:
                if param in kwargs:
                    data[param] = kwargs[param]

            if "interval" in kwargs and self.name == "flux-pro":
                data["interval"] = kwargs["interval"]

            response = await self._async_send_request(endpoint, data)
            task_id = response["id"]

            max_wait_time = kwargs.get("max_wait_time", 300)
            check_interval = kwargs.get("check_interval", 10)
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                result = await self._async_get_result(task_id)
                if result["status"] == "Ready":
                    return result["result"]["sample"]
                elif result["status"] in [
                    "Error",
                    "Request Moderated",
                    "Content Moderated",
                ]:
                    raise Exception(f"Task failed with status: {result['status']}")
                await asyncio.sleep(check_interval)

            raise TimeoutError(
                f"Image generation timed out after {max_wait_time} seconds"
            )
        finally:
            await self._close_async_client()

    def batch_generate(self, prompts: List[str], **kwargs) -> List[Dict]:
        """
        Generates images for a batch of prompts synchronously.

        Args:
            prompts (List[str]): List of text prompts
            **kwargs: Additional arguments passed to generate_image

        Returns:
            List[Dict]: List of result dictionaries
        """
        return [self.generate_image(prompt=prompt, **kwargs) for prompt in prompts]

    async def abatch_generate(
        self, prompts: List[str], max_concurrent: int = 5, **kwargs
    ) -> List[Dict]:
        """
        Asynchronously generates images for a batch of prompts.

        Args:
            prompts (List[str]): List of text prompts
            max_concurrent (int): Maximum number of concurrent tasks
            **kwargs: Additional arguments passed to agenerate_image

        Returns:
            List[Dict]: List of result dictionaries
        """
        try:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_prompt(prompt):
                async with semaphore:
                    return await self.agenerate_image(prompt=prompt, **kwargs)

            tasks = [process_prompt(prompt) for prompt in prompts]
            return await asyncio.gather(*tasks)
        finally:
            await self._close_async_client()

    def __del__(self):
        """Cleanup method to ensure clients are closed."""
        self._client.close()
        if self._async_client is not None and not self._async_client.is_closed:
            with contextlib.suppress(Exception):
                asyncio.run(self._close_async_client())
