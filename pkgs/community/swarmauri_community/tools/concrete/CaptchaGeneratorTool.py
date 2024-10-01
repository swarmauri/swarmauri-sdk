# standard/tools/concrete/CaptchaGeneratorTool.py
import base64
from typing import List, Literal, Dict
from captcha.image import ImageCaptcha
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class CaptchaGeneratorTool(ToolBase):
    type: Literal["CaptchaGeneratorTool"] = "CaptchaGeneratorTool"
    name: str = Field(
        "CaptchaGeneratorTool", description="Tool to generate CAPTCHA images."
    )
    description: str = Field(
        "This tool generates CAPTCHA images from input text and saves them to a specified file.",
        description="Description of the CaptchaGeneratorTool",
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text to encode in the CAPTCHA.",
                required=True,
            ),
        ]
    )

    def __call__(self, text: str) -> Dict[str, str]:
        # Generate CAPTCHA
        image = ImageCaptcha()
        data = image.generate(text)

        # Encode image to base64
        image_b64 = base64.b64encode(data.getvalue()).decode()

        # Create dictionary with encoded image
        result = {"image_b64": image_b64}

        return result
