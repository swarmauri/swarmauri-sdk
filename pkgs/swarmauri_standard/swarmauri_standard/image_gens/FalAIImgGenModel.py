import asyncio
import time
from typing import Any, Dict, List, Literal, Optional

import httpx
from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase

from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ImageGenBase, "FalAIImgGenModel")
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
        "fal-ai/flux-pro/v1.1-ultra-finetuned",
        "fal-ai/minimax-image",
        "fal-ai/aura-flow",
        "fal-ai/flux/dev",
        "fal-ai/flux-lora",
        "fal-ai/flux-lora/inpainting",
        "fal-ai/flux/schnell",
        "fal-ai/flux-pro/v1.1",
        "fal-ai/flux-pro/new",
        "fal-ai/sana",
        "fal-ai/omnigen-v1",
        "fal-ai/lumina-image/v2",
        "fal-ai/stable-diffusion-v35-large",
        "fal-ai/switti",
        "fal-ai/switti/512",
        "fal-ai/recraft-20b",
        "fal-ai/ideogram/v2/turbo",
        "fal-ai/ideogram/v2a",
        "fal-ai/ideogram/v2a/turbo",
        "fal-ai/bria/text-to-image/base",
        "fal-ai/bria/text-to-image/fast",
        "fal-ai/bria/text-to-image/hd",
        "fal-ai/flux-control-lora-canny",
        "fal-ai/flux-control-lora-depth",
        "fal-ai/flux-general",
        "rundiffusion-fal/juggernaut-flux/base",
        "rundiffusion-fal/juggernaut-flux/lightning",
        "rundiffusion-fal/juggernaut-flux/pro",
        "rundiffusion-fal/juggernaut-flux-lora",
        "rundiffusion-fal/rundiffusion-photo-flux",
        "fal-ai/stable-diffusion-v3-medium",
        "fal-ai/fast-sdxl",
        "fal-ai/lora",
        "fal-ai/imagen3/fast",
        "fal-ai/imagen3",
        "fal-ai/janus",
        "fal-ai/sdxl-controlnet-union",
        "fal-ai/kolors",
        "fal-ai/stable-cascade/sote-diffusion",
        "fal-ai/lightning-models",
        "fal-ai/realistic-vision",
        "fal-ai/dreamshaper",
        "fal-ai/pixart-sigma",
        "fal-ai/stable-diffusion-v15",
        "fal-ai/layer-diffusion",
        "fal-ai/fast-fooocus-sdxl/image-to-image",
        "fal-ai/fast-fooocus-sdxl",
        "fal-ai/fooocus/inpaint",
        "fal-ai/fooocus/image-prompt",
        "fal-ai/fooocus/upscale-or-vary",
        "fal-ai/diffusion-edge",
        "fal-ai/fast-sdxl-controlnet-canny",
        "fal-ai/illusion-diffusion",
        "fal-ai/fooocus",
        "fal-ai/lcm",
        "fal-ai/playground-v25",
        "fal-ai/hyper-sdxl",
        "fal-ai/fast-lightning-sdxl",
        "fal-ai/fast-lcm-diffusion",
        "fal-ai/flowedit",
        "fal-ai/stable-cascade",
        "fal-ai/luma-photon",
        "fal-ai/luma-photon/flash",
        "fal-ai/cogview4",
        "fal-ai/fast-turbo-diffusion",
    ]
    api_key: SecretStr = Field(default=None)
    name: str = "fal-ai/flux-pro/v1.1-ultra-finetuned"
    timeout: float = 600.0
    type: Literal["FalAIImgGenModel"] = "FalAIImgGenModel"
    max_retries: int = Field(default=60)  # Maximum number of status check retries
    retry_delay: float = Field(default=1.0)  # Delay between status checks in seconds

    def __init__(self, **kwargs: Dict[str, Any]):
        """
        Initializes the model with the specified API key and model name.

        Args:
            **kwargs (Dict[str, Any]): Additional keyword arguments, which may includes api_key and allowed_models.

        Raises:
            ValueError: If an invalid model name is provided.
        """
        super().__init__(**kwargs)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {self.api_key.get_secret_value()}",
        }
        self._client = httpx.Client(headers=self._headers, timeout=self.timeout)

    async def _get_async_client(self) -> httpx.AsyncClient:
        """
        Get or create the async client.

        Returns:
            httpx.AsyncClient: The async HTTP client instance.
        """
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                headers=self._headers, timeout=self.timeout
            )
        return self._async_client

    async def _close_async_client(self):
        """
        Safely close the async client if it exists and is open.
        """
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None

    def _create_request_payload(self, prompt: str, **kwargs: Dict[str, Any]) -> dict:
        """
        Creates a payload for the image generation request.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs (Dict[str, Any]): Additional parameters for the request.

        Returns:
            dict: The request payload.
        """
        return {"prompt": prompt, **kwargs}

    @retry_on_status_codes((429, 529), max_retries=1)
    def _send_request(self, prompt: str, **kwargs: Dict[str, Any]) -> Dict:
        """
        Sends an image generation request to the queue and returns the request ID.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs (Dict[str, Any]): Additional parameters for the request.

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
    async def _async_send_request(self, prompt: str, **kwargs: Dict[str, Any]) -> Dict:
        """
        Asynchronously sends an image generation request to the queue.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs (Dict[str, Any]): Additional parameters for the request.

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

    def generate_image(self, prompt: str, **kwargs: Dict[str, Any]) -> str:
        """
        Generates an image based on the prompt and returns the image URL.

        Args:
            prompt (str): The text prompt for image generation.
            **kwargs (Dict[str, Any]): Additional parameters for the request.

        Returns:
            str: The URL of the generated image.
        """
        initial_response = self._send_request(prompt, **kwargs)
        request_id = initial_response["request_id"]
        final_response = self._wait_for_completion(request_id)
        return final_response["images"][0]["url"]

    async def agenerate_image(self, prompt: str, **kwargs: Dict[str, Any]) -> str:
        """
        Asynchronously generates an image based on the prompt and returns the image URL.

        Args:
            prompt (str): The text prompt for image generation
            **kwargs (Dict[str, Any]): Additional parameters to pass to the API

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

    def batch_generate(self, prompts: List[str], **kwargs: Dict[str, Any]) -> List[str]:
        """
        Generates images for a batch of prompts.

        Args:
            prompts (List[str]): List of text prompts
            **kwargs (Dict[str, Any]): Additional parameters to pass to the API

        Returns:
            List[str]: List of image URLs
        """
        return [self.generate_image(prompt, **kwargs) for prompt in prompts]

    async def abatch_generate(
        self, prompts: List[str], max_concurrent: int = 5, **kwargs: Dict[str, Any]
    ) -> List[str]:
        """
        Asynchronously generates images for a batch of prompts.

        Args:
            prompts (List[str]): List of text prompts
            max_concurrent (int): Maximum number of concurrent requests
            **kwargs (Dict[str, Any]): Additional parameters to pass to the API

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

    def get_allowed_models(self) -> List[str]:
        """
        Queries the LLMProvider API endpoint to get the list of allowed models.

        Returns:
            List[str]: List of allowed model names.
        """
        return [
            "fal-ai/flux-pro/v1.1-ultra-finetuned",
            "fal-ai/minimax-image",
            "fal-ai/aura-flow",
            "fal-ai/flux/dev",
            "fal-ai/flux-lora",
            "fal-ai/flux-lora/inpainting",
            "fal-ai/flux/schnell",
            "fal-ai/flux-pro/v1.1",
            "fal-ai/flux-pro/new",
            "fal-ai/sana",
            "fal-ai/omnigen-v1",
            "fal-ai/lumina-image/v2",
            "fal-ai/stable-diffusion-v35-large",
            "fal-ai/switti",
            "fal-ai/switti/512",
            "fal-ai/recraft-20b",
            "fal-ai/ideogram/v2/turbo",
            "fal-ai/ideogram/v2a",
            "fal-ai/ideogram/v2a/turbo",
            "fal-ai/bria/text-to-image/base",
            "fal-ai/bria/text-to-image/fast",
            "fal-ai/bria/text-to-image/hd",
            "fal-ai/flux-control-lora-canny",
            "fal-ai/flux-control-lora-depth",
            "fal-ai/flux-general",
            "rundiffusion-fal/juggernaut-flux/base",
            "rundiffusion-fal/juggernaut-flux/lightning",
            "rundiffusion-fal/juggernaut-flux/pro",
            "rundiffusion-fal/juggernaut-flux-lora",
            "rundiffusion-fal/rundiffusion-photo-flux",
            "fal-ai/stable-diffusion-v3-medium",
            "fal-ai/fast-sdxl",
            "fal-ai/lora",
            "fal-ai/imagen3/fast",
            "fal-ai/imagen3",
            "fal-ai/janus",
            "fal-ai/sdxl-controlnet-union",
            "fal-ai/kolors",
            "fal-ai/stable-cascade/sote-diffusion",
            "fal-ai/lightning-models",
            "fal-ai/realistic-vision",
            "fal-ai/dreamshaper",
            "fal-ai/pixart-sigma",
            "fal-ai/stable-diffusion-v15",
            "fal-ai/layer-diffusion",
            "fal-ai/fast-fooocus-sdxl/image-to-image",
            "fal-ai/fast-fooocus-sdxl",
            "fal-ai/fooocus/inpaint",
            "fal-ai/fooocus/image-prompt",
            "fal-ai/fooocus/upscale-or-vary",
            "fal-ai/diffusion-edge",
            "fal-ai/fast-sdxl-controlnet-canny",
            "fal-ai/illusion-diffusion",
            "fal-ai/fooocus",
            "fal-ai/lcm",
            "fal-ai/playground-v25",
            "fal-ai/hyper-sdxl",
            "fal-ai/fast-lightning-sdxl",
            "fal-ai/fast-lcm-diffusion",
            "fal-ai/flowedit",
            "fal-ai/stable-cascade",
            "fal-ai/luma-photon",
            "fal-ai/luma-photon/flash",
            "fal-ai/cogview4",
            "fal-ai/fast-turbo-diffusion",
        ]
