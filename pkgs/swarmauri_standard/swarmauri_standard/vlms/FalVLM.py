import asyncio
import time
from typing import Any, Dict, List, Literal

import httpx
from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase

from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(VLMBase, "FalVLM")
class FalVLM(VLMBase):
    """
    A model for processing images and answering questions using FalAI's vision models.
    This model allows synchronous and asynchronous requests for image processing
    and question answering based on an input image and text prompt.

    Attributes:
        allowed_models (List[str]): List of allowed vision models.
        api_key (str): The API key for authentication.
        name (str): The model name to use for image processing.
        type (Literal): The type identifier for the model.
        max_retries (int): Maximum number of retries for status polling.
        retry_delay (float): Delay in seconds between retries.

    Link to API KEY: https://fal.ai/dashboard/keys
    Link to Allowed Models: https://fal.ai/models?categories=vision
    """

    _BASE_URL: str = PrivateAttr("https://queue.fal.run")
    _client: httpx.Client = PrivateAttr()
    _header: Dict[str, str] = PrivateAttr()

    allowed_models: List[str] = [
        "fal-ai/got-ocr/v2",
        "fal-ai/any-llm/vision",
        "fal-ai/llavav15-13b",
        "fal-ai/llava-next",
        "fal-ai/imageutils/nsfw",
        "fal-ai/moondream/batched",
        "fal-ai/florence-2-large/caption",
        "fal-ai/florence-2-large/detailed-caption",
        "fal-ai/florence-2-large/more-detailed-caption",
        "fal-ai/florence-2-large/region-to-category",
        "fal-ai/florence-2-large/ocr",
        "fal-ai/sa2va/8b/image",
        "fal-ai/sa2va/8b/video",
        "fal-ai/sa2va/4b/video",
        "fal-ai/sa2va/4b/image",
        "fal-ai/mini-cpm",
        "fal-ai/moondream-next",
        "fal-ai/moondream-next/batch",
    ]
    api_key: SecretStr
    name: str = Field(default="fal-ai/got-ocr/v2")
    type: Literal["FalVLM"] = "FalVLM"
    max_retries: int = Field(default=60)
    retry_delay: float = Field(default=1.0)

    def __init__(self, **data: dict[str, Any]) -> None:
        """
        Initialize the FalOCR with API key, HTTP clients, and model name validation.

        Raises:
            ValueError: If the provided name is not in allowed_models.
        """
        super().__init__(**data)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {self.api_key.get_secret_value()}",
        }
        self._client = httpx.Client(headers=self._headers, timeout=30)

    @retry_on_status_codes((429, 529), max_retries=1)
    def _send_request(
        self, image_url: str, prompt: str, **kwargs: dict[str, Any]
    ) -> Dict:
        """
        Send a synchronous request to the vision model API for image processing.

        Args:
            image_url (str): The URL of the image to process.
            prompt (str): The question or instruction to apply to the image.
            **kwargs (dict[str, Any]): Additional parameters for the API request.

        Returns:
            Dict: The result of the image processing request.
        """
        url = f"{self._BASE_URL}/{self.name}"
        payload = {"image_url": image_url, "prompt": prompt, **kwargs}

        response = self._client.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()

        # Handle both immediate completion and queued scenarios
        if "request_id" in response_data:
            return self._wait_for_completion(response_data["request_id"])
        return response_data  # For immediate responses

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_send_request(
        self, image_url: str, prompt: str, **kwargs: dict[str, Any]
    ) -> Dict:
        """
        Send an asynchronous request to the vision model API for image processing.

        Args:
            image_url (str): The URL of the image to process.
            prompt (str): The question or instruction to apply to the image.
            **kwargs: dict[str, Any]: Additional parameters for the API request.

        Returns:
            Dict: The result of the image processing request.
        """
        url = f"{self._BASE_URL}/{self.name}"
        payload = {"image_url": image_url, "prompt": prompt, **kwargs}
        async with httpx.AsyncClient(headers=self._headers, timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            response_data = response.json()
        # Handle both immediate completion and queued scenarios
        if "request_id" in response_data:
            return await self._async_wait_for_completion(response_data["request_id"])
        return response_data  # For immediate responses

    @retry_on_status_codes((429, 529), max_retries=1)
    def _check_status(self, request_id: str) -> Dict:
        """
        Check the status of a queued request.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict: The status response.
        """
        url = f"{self._BASE_URL}/{self.name}/requests/{request_id}/status"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_check_status(self, request_id: str) -> Dict:
        """
        Asynchronously check the status of a queued request.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict: The status response.
        """
        url = f"{self._BASE_URL}/{self.name}/requests/{request_id}/status"
        async with httpx.AsyncClient(headers=self._headers, timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    @retry_on_status_codes((429, 529), max_retries=1)
    def _wait_for_completion(self, request_id: str) -> Dict:
        for _ in range(self.max_retries):
            status_data = self._check_status(request_id)
            if status_data.get("status") == "COMPLETED":
                response = self._client.get(status_data.get("response_url"))
                response.raise_for_status()
                return response.json()
            elif status_data.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                time.sleep(self.retry_delay)
            else:
                raise RuntimeError(f"Unexpected status: {status_data}")

        raise TimeoutError(
            f"Request {request_id} did not complete within the timeout period"
        )

    @retry_on_status_codes((429, 529), max_retries=1)
    async def _async_wait_for_completion(self, request_id: str) -> Dict:
        for _ in range(self.max_retries):
            status_data = await self._async_check_status(request_id)
            if status_data.get("status") == "COMPLETED":
                async with httpx.AsyncClient(
                    headers=self._headers, timeout=30
                ) as client:
                    response = await client.get(status_data.get("response_url"))
                    response.raise_for_status()
                    return response.json()
            elif status_data.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                await asyncio.sleep(self.retry_delay)
            else:
                raise RuntimeError(f"Unexpected status: {status_data}")

        raise TimeoutError(
            f"Request {request_id} did not complete within the timeout period"
        )

    def predict_vision(
        self, image_url: str, prompt: str, **kwargs: dict[str, Any]
    ) -> str:
        """
        Process an image and answer a question based on the prompt.

        Args:
            image_url (str): The URL of the image to process.
            prompt (str): The question or instruction to apply to the image.
            **kwargs (dict[str, Any]): Additional parameters for the API request.

        Returns:
            str: The answer or result of the image processing.
        """
        response_data = self._send_request(image_url, prompt, **kwargs)
        return response_data.get("output", "")

    async def apredict_vision(
        self, image_url: str, prompt: str, **kwargs: dict[str, Any]
    ) -> str:
        """
        Asynchronously process an image and answer a question based on the prompt.

        Args:
            image_url (str): The URL of the image to process.
            prompt (str): The question or instruction to apply to the image.
            **kwargs (dict[str, Any]): Additional parameters for the API request.

        Returns:
            str: The answer or result of the image processing.
        """
        response_data = await self._async_send_request(image_url, prompt, **kwargs)
        return response_data.get("output", "")

    def batch(
        self, image_urls: List[str], prompts: List[str], **kwargs: dict[str, Any]
    ) -> List[str]:
        """
        Process a batch of images and answer questions for each image synchronously.

        Args:
            image_urls (List[str]): A list of image URLs to process.
            prompts (List[str]): A list of prompts corresponding to each image.
            **kwargs (dict[str, Any]): Additional parameters for the API requests.

        Returns:
            List[str]: A list of answers or results for each image.
        """
        return [
            self.predict_vision(image_url, prompt, **kwargs)
            for image_url, prompt in zip(image_urls, prompts)
        ]

    async def abatch(
        self, image_urls: List[str], prompts: List[str], **kwargs: dict[str, Any]
    ) -> List[str]:
        """
        Asynchronously process a batch of images and answer questions for each image.

        Args:
            image_urls (List[str]): A list of image URLs to process.
            prompts (List[str]): A list of prompts corresponding to each image.
            **kwargs: (dict[str, Any]): Additional parameters for the API requests.

        Returns:
            List[str]: A list of answers or results for each image.

        Raises:
            TimeoutError: If one or more requests do not complete within the timeout period.
        """
        tasks = [
            self.apredict_vision(image_url, prompt, **kwargs)
            for image_url, prompt in zip(image_urls, prompts)
        ]
        return await asyncio.gather(*tasks)

    def get_allowed_models(self) -> List[str]:
        """
        Query the LLMProvider API endpoint to get the list of allowed models.

        Returns:
            List[str]: The list of allowed models from the API.
        """
        url = "https://fal.ai/models?categories=vision"
        response = self._client.get(url)
        response.raise_for_status()
        models_data = response.json()
        return models_data.get("models", [])
