
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_captchagenerator/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_captchagenerator" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_captchagenerator/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_captchagenerator.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_captchagenerator/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_captchagenerator" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_captchagenerator/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_captchagenerator" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_captchagenerator/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_captchagenerator?label=swarmauri_tool_captchagenerator&color=green" alt="PyPI - swarmauri_tool_captchagenerator"/></a>
</p>

---

# Swarmauri Tool Captcha Generator

This tool generates CAPTCHA images from input text and saves them to a specified file.

## Installation

```bash
pip install swarmauri_tool_captchagenerator
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.tools.CaptchaGeneratorTool import CaptchaGeneratorTool

# Initialize the tool
tool = CaptchaGeneratorTool()

# Sample text for CAPTCHA generation
text = "This is a test CAPTCHA"

# Generate CAPTCHA
result = tool(text)

# Access the base64 encoded image
image_b64 = result["image_b64"]
print(image_b64)
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
