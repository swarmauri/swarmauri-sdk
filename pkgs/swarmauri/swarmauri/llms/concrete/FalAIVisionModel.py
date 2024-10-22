import os
import fal_client
import asyncio
from typing import List, Literal, Optional, Union, Dict
from pydantic import Field, ConfigDict
from swarmauri.llms.base.LLMBase import LLMBase


class FalAIVisionModel(LLMBase):
    """
    A model for processing images and answering questions using vision models provided by FalAI.
    Get your API KEY here: https://fal.ai/dashboard/keys
    """

    allowed_models: List[str] = [
        "fal-ai/llava-next",
        "fal-ai/llavav15-13b",
        "fal-ai/any-llm/vision",
    ]
    api_key: str = Field(default_factory=lambda: os.environ.get("FAL_KEY"))
    model_name: str = Field(default="fal-ai/llava-next")
    type: Literal["FalAIVisionModel"] = "FalAIVisionModel"

    model_config = ConfigDict(protected_namespaces=())

    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key:
            os.environ["FAL_KEY"] = self.api_key
        if self.model_name not in self.allowed_models:
            raise ValueError(
                f"Invalid model name. Allowed models are: {', '.join(self.allowed_models)}"
            )

    def _send_request(self, image_url: str, prompt: str, **kwargs) -> Dict:
        """Send a request to the vision model API for image processing and question answering."""
        arguments = {"image_url": image_url, "prompt": prompt, **kwargs}
        result = fal_client.subscribe(
            self.model_name,
            arguments=arguments,
            with_logs=True,
        )
        return result

    def process_image(self, image_url: str, prompt: str, **kwargs) -> str:
        """Process an image and answer a question based on the prompt."""
        response_data = self._send_request(image_url, prompt, **kwargs)
        return response_data["output"]

    async def aprocess_image(self, image_url: str, prompt: str, **kwargs) -> str:
        """Asynchronously process an image and answer a question based on the prompt."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.process_image, image_url, prompt, **kwargs
        )

    def batch(self, image_urls: List[str], prompts: List[str], **kwargs) -> List[str]:
        """
        Process a batch of images and answer questions for each.
        Returns a list of answers.
        """
        answers = []
        for image_url, prompt in zip(image_urls, prompts):
            answer = self.process_image(image_url=image_url, prompt=prompt, **kwargs)
            answers.append(answer)
        return answers

    async def abatch(
        self,
        image_urls: List[str],
        prompts: List[str],
        max_concurrent: int = 5,
        **kwargs,
    ) -> List[str]:
        """
        Asynchronously process a batch of images and answer questions for each.
        Returns a list of answers.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_image_prompt(image_url, prompt):
            async with semaphore:
                return await self.aprocess_image(
                    image_url=image_url, prompt=prompt, **kwargs
                )

        tasks = [
            process_image_prompt(image_url, prompt)
            for image_url, prompt in zip(image_urls, prompts)
        ]
        return await asyncio.gather(*tasks)

    @staticmethod
    def upload_file(file_path: str) -> str:
        """Upload a file and return the URL."""
        return fal_client.upload_file(file_path)
