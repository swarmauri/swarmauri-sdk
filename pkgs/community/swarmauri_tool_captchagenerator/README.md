![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

Tool that generates CAPTCHA images from text using the [`captcha`](https://pypi.org/project/captcha/) library. Returns the rendered PNG as a base64-encoded string so it can be stored or embedded inline.

## Features

- Accepts a single parameter (`text`) and produces an ImageCaptcha output.
- Returns a dictionary with `image_b64` containing the PNG bytes encoded as base64.
- Can be wired into larger Swarmauri toolchains to produce human challenges dynamically.

## Prerequisites

- Python 3.10 or newer.
- Pillow and captcha dependencies (installed automatically with this package).

## Installation

```bash
# pip
pip install swarmauri_tool_captchagenerator

# poetry
poetry add swarmauri_tool_captchagenerator

# uv (pyproject-based projects)
uv add swarmauri_tool_captchagenerator
```

## Quickstart

```python
import base64
from pathlib import Path
from swarmauri_tool_captchagenerator import CaptchaGeneratorTool

captcha_tool = CaptchaGeneratorTool()
result = captcha_tool("Verify42")

image_b64 = result["image_b64"]
image_bytes = base64.b64decode(image_b64)
Path("captcha.png").write_bytes(image_bytes)
```

Displaying inline (e.g., in a HTML response):

```python
html = f"<img src='data:image/png;base64,{image_b64}' alt='captcha' />"
```

## Tips

- Customize CAPTCHA rendering (fonts, size) by subclassing and configuring `ImageCaptcha` (e.g., `ImageCaptcha(width=280, height=90)`).
- Store the generated solution (`Verify42` in the example) securely server-side to validate client responses later.
- For high throughput, reuse the tool instance rather than instantiating per request to avoid repeated font loading overhead.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
