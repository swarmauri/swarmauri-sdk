
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_zapierhook" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_zapierhook/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_zapierhook/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_zapierhook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_zapierhook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_zapierhook?label=swarmauri_tool_zapierhook&color=green" alt="PyPI - swarmauri_tool_zapierhook"/></a>
</p>

---

# Swarmauri Tool Zapier Hook

A tool for integrating Zapier webhooks with Swarmauri, enabling automated workflows through Zapier's API.

## Installation

```bash
pip install swarmauri_tool_zapierhook
```

## Usage

Here's a basic example of how to use the Zapier Hook Tool:

```python
from swarmauri.tools.ZapierHookTool import ZapierHookTool

# Initialize the tool with your Zapier webhook URL
zapier_tool = ZapierHookTool(zap_url="your_zapier_webhook_url")

# Send a payload to trigger the Zap
payload = '{"message": "Hello from Swarmauri!"}'
response = zapier_tool(payload)

# The response will contain the Zapier API response
print(response['zap_response'])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

