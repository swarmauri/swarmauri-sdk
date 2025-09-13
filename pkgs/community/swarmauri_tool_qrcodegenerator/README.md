
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_qrcodegenerator" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_qrcodegenerator/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_qrcodegenerator.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_qrcodegenerator" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_qrcodegenerator" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_qrcodegenerator?label=swarmauri_tool_qrcodegenerator&color=green" alt="PyPI - swarmauri_tool_qrcodegenerator"/></a>
</p>

---

# Swarmauri Tool Qrcodegenerator

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

