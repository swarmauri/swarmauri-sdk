import httpx
import asyncio
from typing import List, Literal, Optional, Dict
from pydantic import Field, PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
import time


class FalAIImgGenModel(ImageGenBase):
    """
    A model class for generating images from text using FluxPro's image generation model,
    provided by FalAI. This class uses a queue-based API to handle image generation requests.

    Attributes:
        allowed_models (List[str]): List of valid model names for image generation.
        api_key (str): The API key for authenticating requests with the FalAI service.
        model_name (str): The name of the model used for image generation.
        type (Literal): The model type, fixed as "FalAIImgGenModel".
        max_retries (int): The maximum number of retries for polling request status.
        retry_delay (float): Delay in seconds between status check retries.
    """

    _BASE_URL: str = PrivateAttr("https://queue.fal.run")
    _client: httpx.Client = PrivateAttr()
    _async_client: Optional[httpx.AsyncClient] = PrivateAttr(default=None)

    allowed_models: List[str] = [
        "fal-ai/flux-pro",
    ]
    api_key: str = Field(default=None)
    name: str = Field(default="fal-ai/flux-pro")
    type: Literal["FalAIImgGenModel"] = "FalAIImgGenModel"
    max_retries: int = Field(default=60)  # Maximum number of status check retries
    retry_delay: float = Field(default=1.0)  # Delay between status checks in seconds

    def __init__(self, **kwargs):
        """
        Initializes the model with the specified API key and model name.

        Args:
            **data: Configuration parameters for the model.

        Raises:
            ValueError: If an invalid model name is provided.
        """
        super().__init__(**kwargs)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {self.api_key}",
        }
        self._client = httpx.Client(headers=self._headers, timeout=30)

    async def _get_async_client(self) -> httpx.AsyncClient:
        """
        Get or create the async client.

        Returns:
            httpx.AsyncClient: The async HTTP client instance.
        """
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(headers=self._headers, timeout=30)
        return self._async_client

    async def _close_async_client(self):
        """
        Safely close the async client if it exists and is open.
        """
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None

    def _create_request_payload(self, prompt: str, **kwargs) -> dict:
        """
        Creates a payload for the image generation request.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs: Additional parameters for the request.

        Returns:
            dict: The request payload.
        """
        return {"prompt": prompt, **kwargs}

    @retry_on_status_codes((429, 529), max_retries=1)
    def _send_request(self, prompt: str, **kwargs) -> Dict:
        """
        Sends an image generation request to the queue and returns the request ID.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs: Additional parameters for the request.

        Returns:
            Dict: The response containing the request ID.
        """
        url = f"{self._BASE_URL}/{self.name}"
        payload = self._create_request_payload(prompt, **kwargs)

        response = self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    def _check_status(self, request_id: str) -> Dict:
        """
        Checks the status of a queued image generation request.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict: The response containing the request status.
        """
        url = f"{self._BASE_URL}/{self.name}/requests/{request_id}/status"
        response = self._client.get(url, params={"logs": 1})
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    def _get_result(self, request_id: str) -> Dict:
        """
        Retrieves the final result of a completed request.

        Args:
            request_id (str): The ID of the completed request.

        Returns:
            Dict: The response containing the generated image URL.
        """
        url = f"{self._BASE_URL}/{self.name}/requests/{request_id}"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_send_request(self, prompt: str, **kwargs) -> Dict:
        """
        Asynchronously sends an image generation request to the queue.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs: Additional parameters for the request.

        Returns:
            Dict: The response containing the request ID.
        """
        client = await self._get_async_client()
        url = f"{self._BASE_URL}/{self.name}"
        payload = self._create_request_payload(prompt, **kwargs)

        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_check_status(self, request_id: str) -> Dict:
        """
        Asynchronously checks the status of a queued request.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict: The response containing the request status.
        """
        client = await self._get_async_client()
        url = f"{self._BASE_URL}/{self.name}/requests/{request_id}/status"
        response = await client.get(url, params={"logs": 1})
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_get_result(self, request_id: str) -> Dict:
        """
        Asynchronously retrieves the final result of a completed request.

        Args:
            request_id (str): The ID of the completed request.

        Returns:
            Dict: The response containing the generated image URL.
        """
        client = await self._get_async_client()
        url = f"{self._BASE_URL}/{self.name}/requests/{request_id}"
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

    def _wait_for_completion(self, request_id: str) -> Dict:
        """
        Waits for a request to complete, polling the status endpoint.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict: The final response containing the generated image URL.

        Raises:
            TimeoutError: If the request does not complete within the retry limit.
        """
        for _ in range(self.max_retries):
            status_data = self._check_status(request_id)
            if status_data["status"] == "COMPLETED":
                return self._get_result(request_id)
            elif status_data["status"] in ["IN_QUEUE", "IN_PROGRESS"]:
                time.sleep(self.retry_delay)
            else:
                raise RuntimeError(f"Unexpected status: {status_data}")

        raise TimeoutError(
            f"Request {request_id} did not complete within the timeout period"
        )

    async def _async_wait_for_completion(self, request_id: str) -> Dict:
        """
        Asynchronously waits for a request to complete, polling the status endpoint.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict: The final response containing the generated image URL.

        Raises:
            TimeoutError: If the request does not complete within the retry limit.
        """
        for _ in range(self.max_retries):
            status_data = await self._async_check_status(request_id)
            if status_data["status"] == "COMPLETED":
                return await self._async_get_result(request_id)
            elif status_data["status"] in ["IN_QUEUE", "IN_PROGRESS"]:
                await asyncio.sleep(self.retry_delay)
            else:
                raise RuntimeError(f"Unexpected status: {status_data}")

        raise TimeoutError(
            f"Request {request_id} did not complete within the timeout period"
        )

    def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Generates an image based on the prompt and returns the image URL.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs: Additional parameters for the request.

        Returns:
            str: The URL of the generated image.
        """
        initial_response = self._send_request(prompt, **kwargs)
        request_id = initial_response["request_id"]
        final_response = self._wait_for_completion(request_id)
        return final_response["images"][0]["url"]

    async def agenerate_image(self, prompt: str, **kwargs) -> str:
        """
        Asynchronously generates an image based on the prompt and returns the image URL.

        Args:
            prompt (str): The text prompt for image generation
            **kwargs: Additional parameters to pass to the API

        Returns:
            str: The URL of the generated image
        """
        try:
            initial_response = await self._async_send_request(prompt, **kwargs)
            request_id = initial_response["request_id"]
            final_response = await self._async_wait_for_completion(request_id)
            return final_response["images"][0]["url"]
        finally:
            await self._close_async_client()

    def batch(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Generates images for a batch of prompts.

        Args:
            prompts (List[str]): List of text prompts
            **kwargs: Additional parameters to pass to the API

        Returns:
            List[str]: List of image URLs
        """
        return [self.generate_image(prompt, **kwargs) for prompt in prompts]

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
        try:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_prompt(prompt):
                async with semaphore:
                    initial_response = await self._async_send_request(prompt, **kwargs)
                    request_id = initial_response["request_id"]
                    final_response = await self._async_wait_for_completion(request_id)
                    return final_response["response"]["images"][0]["url"]

            tasks = [process_prompt(prompt) for prompt in prompts]
            return await asyncio.gather(*tasks)
        finally:
            await self._close_async_client()

    def __del__(self):
        """Cleanup method to close HTTP clients."""
        self._client.close()
