# standard/tools/concrete/CaptchaGeneratorTool.py
import base64
from typing import List, Literal, Dict
from captcha.image import ImageCaptcha
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "CaptchaGeneratorTool")
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
                input_type="string",
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
