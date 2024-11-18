import os
import httpx
import asyncio
from typing import List, Literal, Optional, Dict
from pydantic import Field, ConfigDict, PrivateAttr
from swarmauri.llms.base.LLMBase import LLMBase
import time


class FalAIVisionModel(LLMBase):
    _BASE_URL: str = PrivateAttr("https://queue.fal.run")
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()

    allowed_models: List[str] = [
        "fal-ai/llava-next",
    ]
    api_key: str = Field(default_factory=lambda: os.environ.get("FAL_KEY"))
    model_name: str = Field(default="fal-ai/llava-next")
    type: Literal["FalAIVisionModel"] = "FalAIVisionModel"
    max_retries: int = Field(default=60)
    retry_delay: float = Field(default=1.0)

    model_config = ConfigDict(protected_namespaces=())

    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key:
            os.environ["FAL_KEY"] = self.api_key
        if self.model_name not in self.allowed_models:
            raise ValueError(
                f"Invalid model name. Allowed models are: {', '.join(self.allowed_models)}"
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {self.api_key}",
        }
        self._client = httpx.Client(headers=headers)
        self._async_client = httpx.AsyncClient(headers=headers)

    def _send_request(self, image_url: str, prompt: str, **kwargs) -> Dict:
        url = f"{self._BASE_URL}/{self.model_name}"
        payload = {"image_url": image_url, "prompt": prompt, **kwargs}

        response = self._client.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()

        # Handle both immediate completion and queued scenarios
        if "request_id" in response_data:
            return self._wait_for_completion(response_data["request_id"])
        return response_data  # For immediate responses

    async def _async_send_request(self, image_url: str, prompt: str, **kwargs) -> Dict:
        url = f"{self._BASE_URL}/{self.model_name}"
        payload = {"image_url": image_url, "prompt": prompt, **kwargs}

        async with httpx.AsyncClient(headers=self._async_client.headers) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            response_data = response.json()

            # Handle both immediate completion and queued scenarios
            if "request_id" in response_data:
                return await self._async_wait_for_completion(
                    response_data["request_id"]
                )
            return response_data  # For immediate responses

    def _check_status(self, request_id: str) -> Dict:
        url = f"{self._BASE_URL}/{self.model_name}/requests/{request_id}/status"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    async def _async_check_status(self, request_id: str) -> Dict:
        url = f"{self._BASE_URL}/{self.model_name}/requests/{request_id}/status"
        async with httpx.AsyncClient(headers=self._async_client.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    def _wait_for_completion(self, request_id: str) -> Dict:
        for _ in range(self.max_retries):
            status_data = self._check_status(request_id)
            if status_data.get("status") == "COMPLETED":
                return status_data.get("response", {})
            elif status_data.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                time.sleep(self.retry_delay)
            else:
                raise RuntimeError(f"Unexpected status: {status_data}")

        raise TimeoutError(
            f"Request {request_id} did not complete within the timeout period"
        )

    async def _async_wait_for_completion(self, request_id: str) -> Dict:
        for _ in range(self.max_retries):
            status_data = await self._async_check_status(request_id)
            if status_data.get("status") == "COMPLETED":
                return status_data.get("response", {})
            elif status_data.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
                await asyncio.sleep(self.retry_delay)
            else:
                raise RuntimeError(f"Unexpected status: {status_data}")

        raise TimeoutError(
            f"Request {request_id} did not complete within the timeout period"
        )

    def process_image(self, image_url: str, prompt: str, **kwargs) -> str:
        response_data = self._send_request(image_url, prompt, **kwargs)
        return response_data.get("output", "")

    async def aprocess_image(self, image_url: str, prompt: str, **kwargs) -> str:
        response_data = await self._async_send_request(image_url, prompt, **kwargs)
        return response_data.get("output", "")

    def batch(self, image_urls: List[str], prompts: List[str], **kwargs) -> List[str]:
        return [
            self.process_image(image_url, prompt, **kwargs)
            for image_url, prompt in zip(image_urls, prompts)
        ]

    async def abatch(
        self, image_urls: List[str], prompts: List[str], **kwargs
    ) -> List[str]:
        async with httpx.AsyncClient(headers=self._async_client.headers) as client:
            tasks = [
                self.aprocess_image(image_url, prompt, **kwargs)
                for image_url, prompt in zip(image_urls, prompts)
            ]
            return await asyncio.gather(*tasks)

    def __del__(self):
        self._client.close()
        if not self._async_client.is_closed:
            asyncio.create_task(self._async_client.aclose())
