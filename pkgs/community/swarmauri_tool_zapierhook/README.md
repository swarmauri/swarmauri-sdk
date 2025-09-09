
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_zapierhook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook.svg"/></a>
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

