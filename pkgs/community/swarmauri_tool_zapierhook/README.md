![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_zapierhook)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_zapierhook)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_zapierhook)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_zapierhook?label=swarmauri_tool_zapierhook&color=green)

</div>

---

# Swarmauri Zapier Hook Tool

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

