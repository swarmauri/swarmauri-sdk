import requests
import time
from typing import List, Literal, Optional, Union, Dict
from pydantic import Field
from swarmauri.llms.base.LLMBase import LLMBase
import asyncio
from typing import ClassVar


class BlackForestImgGenModel(LLMBase):
    """
    A model for generating images using FluxPro's image generation models through the Black Forest API.
    Get your API key here: https://api.bfl.ml/auth/profile
    """

    api_key: str
    base_url: str = "https://api.bfl.ml"
    allowed_models: List[str] = ["flux-pro-1.1", "flux-pro", "flux-dev"]

    asyncio: ClassVar = asyncio
    name: str = "flux-pro"  # Default model
    type: Literal["BlackForestImgGenModel"] = "BlackForestImgGenModel"

    def _send_request(self, endpoint: str, data: dict) -> dict:
        """Send a request to FluxPro's API for image generation."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-Key": self.api_key,
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def _get_result(self, task_id: str) -> dict:
        """Get the result of a generation task."""
        url = f"{self.base_url}/v1/get_result"
        params = {"id": task_id}
        headers = {"X-Key": self.api_key}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

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
        Generates an image based on the prompt and waits for the result.

        :param max_wait_time: Maximum time to wait for the result in seconds (default: 300)
        :param check_interval: Time between status checks in seconds (default: 10)
        :return: Dictionary containing the image URL and other result information
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
        """Asynchronously generates an image based on the prompt and waits for the result."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_image, prompt, **kwargs)

    def batch_generate(self, prompts: List[str], **kwargs) -> List[Dict]:
        """
        Generates images for a batch of prompts and waits for all results.
        Returns a list of result dictionaries.
        """
        results = []
        for prompt in prompts:
            results.append(self.generate_image(prompt=prompt, **kwargs))
        return results

    async def abatch_generate(
        self, prompts: List[str], max_concurrent: int = 5, **kwargs
    ) -> List[Dict]:
        """
        Asynchronously generates images for a batch of prompts and waits for all results.
        Returns a list of result dictionaries.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_prompt(prompt):
            async with semaphore:
                return await self.agenerate_image(prompt=prompt, **kwargs)

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
