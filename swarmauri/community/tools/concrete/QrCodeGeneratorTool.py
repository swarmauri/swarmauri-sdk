# standard/tools/concrete/QrCodeGeneratorTool.py
import qrcode
from typing import List, Literal, Dict, Any
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class QrCodeGeneratorTool(ToolBase):
    type: Literal['QrCodeGeneratorTool'] = 'QrCodeGeneratorTool'
    name: str = Field("QrCodeGeneratorTool", description="Tool to generate QR codes.")
    description: str = Field("Generates QR codes from input data.", description="Description of the QrCodeGeneratorTool")
    
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="data",
                type="string",
                description="The data to encode in the QR code.",
                required=True
            ),
            Parameter(
                name="output_file",
                type="string",
                description="The filename where the QR code will be saved.",
                required=True
            )
        ]
    )

    def __call__(self, data: str, output_file: str):
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        img.save(output_file)