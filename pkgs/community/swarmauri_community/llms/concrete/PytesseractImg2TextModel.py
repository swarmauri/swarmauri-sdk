import os
import asyncio
import logging
from typing import List, Literal, Union
from pydantic import Field, ConfigDict
from PIL import Image
import pytesseract
from io import BytesIO
from swarmauri.llms.base.LLMBase import LLMBase


class PytesseractImg2TextModel(LLMBase):
    """
    A model for performing OCR (Optical Character Recognition) using Pytesseract.
    It can process both local images and image bytes, returning extracted text.
    Requires Tesseract-OCR to be installed on the system.
    """

    tesseract_cmd: str = Field(
        default_factory=lambda: os.environ.get(
            "TESSERACT_CMD",
            ("/usr/bin/tesseract" if os.path.exists("/usr/bin/tesseract") else None),
        )
    )
    type: Literal["PytesseractImg2TextModel"] = "PytesseractImg2TextModel"
    language: str = Field(default="eng")
    config: str = Field(default="")  # Custom configuration string
    model_config = ConfigDict(protected_namespaces=())

    def __init__(self, **data):
        super().__init__(**data)
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def _process_image(self, image: Union[str, bytes, Image.Image], **kwargs) -> str:
        """Process an image and return extracted text."""
        try:
            # Handle different input types
            if isinstance(image, str):
                # If image is a file path
                img = Image.open(image)
            elif isinstance(image, bytes):
                # If image is bytes
                img = Image.open(BytesIO(image))
            elif isinstance(image, Image.Image):
                # If image is already a PIL Image
                img = image
            else:
                raise ValueError("Unsupported image format")

            # Extract text using pytesseract
            custom_config = kwargs.get("config", self.config)
            lang = kwargs.get("language", self.language)

            text = pytesseract.image_to_string(img, lang=lang, config=custom_config)

            return text.strip()

        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    def extract_text(self, image: Union[str, bytes, Image.Image], **kwargs) -> str:
        """
        Extracts text from an image.

        Args:
            image: Can be a file path, bytes, or PIL Image
            **kwargs: Additional arguments for OCR processing
                     - language: OCR language (e.g., 'eng', 'fra', etc.)
                     - config: Custom Tesseract configuration string

        Returns:
            Extracted text as string
        """
        return self._process_image(image, **kwargs)

    async def aextract_text(
        self, image: Union[str, bytes, Image.Image], **kwargs
    ) -> str:
        """
        Asynchronously extracts text from an image.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.extract_text, image, **kwargs)

    def batch(
        self, images: List[Union[str, bytes, Image.Image]], **kwargs
    ) -> List[str]:
        """
        Process multiple images in batch.

        Args:
            images: List of images (file paths, bytes, or PIL Images)
            **kwargs: Additional arguments for OCR processing

        Returns:
            List of extracted texts
        """
        results = []
        for image in images:
            text = self.extract_text(image=image, **kwargs)
            results.append(text)
        return results

    async def abatch(
        self,
        images: List[Union[str, bytes, Image.Image]],
        max_concurrent: int = 5,
        **kwargs,
    ) -> List[str]:
        """
        Asynchronously process multiple images in batch.

        Args:
            images: List of images (file paths, bytes, or PIL Images)
            max_concurrent: Maximum number of concurrent operations
            **kwargs: Additional arguments for OCR processing

        Returns:
            List of extracted texts
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_image(image):
            async with semaphore:
                return await self.aextract_text(image=image, **kwargs)

        tasks = [process_image(image) for image in images]
        return await asyncio.gather(*tasks)

    def get_supported_languages(self) -> List[str]:
        """
        Returns a list of supported languages by executing 'tesseract --list-langs' command.

        Returns:
            List[str]: List of available language codes (e.g., ['eng', 'osd'])

        Raises:
            Exception: If the command execution fails or returns unexpected output
        """
        try:
            # Execute tesseract command to list languages
            import subprocess

            result = subprocess.run(
                [self.tesseract_cmd, "--list-langs"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the output
            output_lines = result.stdout.strip().split("\n")

            # Skip the first line which is the directory info
            # and filter out empty lines
            languages = [lang.strip() for lang in output_lines[1:] if lang.strip()]

            return languages

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get language list from Tesseract: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error getting supported languages: {str(e)}")
