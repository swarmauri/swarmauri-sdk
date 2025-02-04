![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_qrcodegenerator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_qrcodegenerator)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_qrcodegenerator)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_qrcodegenerator?label=swarmauri_tool_qrcodegenerator&color=green)

</div>

---

# QR Code Generator Tool

A tool component for generating QR codes from input data. The tool creates QR codes and returns them as base64-encoded images.

## Installation

```bash
pip install swarmauri_tool_qrcodegenerator
```

## Usage

Here's a basic example of how to use the QR Code Generator Tool:

```python
from swarmauri.tools.QrCodeGeneratorTool import QrCodeGeneratorTool

# Initialize the tool
qr_tool = QrCodeGeneratorTool()

# Generate a QR code
result = qr_tool("Hello, world!")

# The result contains the QR code as a base64-encoded string
image_b64 = result['image_b64']
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

