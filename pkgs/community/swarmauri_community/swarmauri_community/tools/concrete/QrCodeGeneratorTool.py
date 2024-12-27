# standard/tools/concrete/QrCodeGeneratorTool.py
import qrcode
from typing import List, Literal, Dict, Any
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
import base64


class QrCodeGeneratorTool(ToolBase):
    type: Literal["QrCodeGeneratorTool"] = "QrCodeGeneratorTool"
    name: str = Field("QrCodeGeneratorTool", description="Tool to generate QR codes.")
    description: str = Field(
        "Generates QR codes from input data.",
        description="Description of the QrCodeGeneratorTool",
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="data",
                type="string",
                description="The data to encode in the QR code.",
                required=True,
            ),
        ]
    )

    def __call__(self, data: str):
        """
        Generate a QR code from the provided data and return the QR code image as a base64-encoded string.

        Parameters:
            data (str): The data to encode in the QR code.

        Returns:
            Dict[str, str]: A dictionary containing the base64-encoded QR code image, with the key 'image_b64'.

        Example:
            >>> tool = QrCodeGeneratorTool()
            >>> result = tool("Hello, world!")
            >>> print(result['image_b64'])  # Prints the base64 string of the QR code image
        """
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")

        # Encode image to base64
        image_bytes = img.tobytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # Create dictionary with encoded image
        result = {"image_b64": image_b64}

        return result
