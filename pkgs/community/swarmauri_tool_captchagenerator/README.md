![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_captchagenerator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_captchagenerator)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_captchagenerator)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_captchagenerator?label=swarmauri_tool_captchagenerator&color=green)

</div>

---

# Swarmauri Captcha Generator Tool

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
