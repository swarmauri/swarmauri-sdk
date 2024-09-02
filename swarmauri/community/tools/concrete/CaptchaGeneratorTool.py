# standard/tools/concrete/CaptchaGeneratorTool.py
from captcha.image import ImageCaptcha
from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class CaptchaGeneratorTool(ToolBase):
    type: Literal['CaptchaGeneratorTool'] = 'CaptchaGeneratorTool'
    name: str = Field("CaptchaGeneratorTool", description="Tool to generate CAPTCHA images.")
    description: str = Field(
        "This tool generates CAPTCHA images from input text and saves them to a specified file.",
        description="Description of the CaptchaGeneratorTool"
    )
    
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text to encode in the CAPTCHA.",
                required=True
            ),
            Parameter(
                name="output_file",
                type="string",
                description="The filename where the CAPTCHA image will be saved.",
                required=True
            )
        ]
    )

    def __call__(self, text: str, output_file: str):
        # Generate CAPTCHA
        image = ImageCaptcha()
        data = image.generate(text)
        image.write(text, output_file)
        #print(f"CAPTCHA image generated and saved to {output_file}")
