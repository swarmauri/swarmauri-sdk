![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_zapierhook/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_zapierhook/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_zapierhook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_zapierhook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_zapierhook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_zapierhook?label=swarmauri_tool_zapierhook&color=green" alt="PyPI - swarmauri_tool_zapierhook"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Zapier Hook

`swarmauri_tool_zapierhook` is a Swarmauri integration tool for posting payloads
to a Zapier catch-hook URL. It is useful for pushing agent outputs into Zapier
automations, handing off events to SaaS workflows, and bridging Swarmauri
systems with no-code operational pipelines.

## Why Use Swarmauri Tool Zapier Hook

- Forward events from Swarmauri into Zapier automations.
- Trigger downstream notifications, CRM updates, tickets, or task flows.
- Keep Zapier integration behind a reusable Swarmauri tool interface.
- Return structured responses from webhook execution.

## FAQ

> **What input does the tool expect at runtime?**  
> A single string `payload`, plus a configured `zap_url` on the tool instance.

> **How is the payload sent?**  
> The tool posts JSON in the shape `{"data": payload}`.

> **What does the tool return?**  
> A dictionary containing `zap_response`.

> **How are webhook failures handled?**  
> Non-200 responses raise the underlying HTTP error.

## Features

- Swarmauri `ToolBase` implementation registered as `ZapierHookTool`.
- Posts JSON payloads to Zapier catch-hook URLs.
- Keeps webhook URL configuration on the tool instance.
- Returns the Zapier response body as serialized JSON.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_zapierhook
```

```bash
pip install swarmauri_tool_zapierhook
```

## Usage

```python
from swarmauri_tool_zapierhook import ZapierHookTool

tool = ZapierHookTool(zap_url="https://hooks.zapier.com/hooks/catch/...")
result = tool('{"event":"demo"}')

print(result["zap_response"])
```

## Examples

### Trigger a Zap from agent output

```python
from swarmauri_tool_zapierhook import ZapierHookTool

tool = ZapierHookTool(zap_url="https://hooks.zapier.com/hooks/catch/...")
payload = '{"lead":"alice@example.com","source":"agent"}'

print(tool(payload))
```

### Send a monitoring alert

```python
from swarmauri_tool_zapierhook import ZapierHookTool

tool = ZapierHookTool(zap_url="https://hooks.zapier.com/hooks/catch/...")
alert = '{"service":"payments","severity":"critical"}'

tool(alert)
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_zapierhook import ZapierHookTool

tools = ToolCollection(
    tools=[ZapierHookTool(zap_url="https://hooks.zapier.com/hooks/catch/...")]
)
print(tools)
```

## Related Packages

- [swarmauri_tool_webscraping](https://pypi.org/project/swarmauri_tool_webscraping/)
- [swarmauri_tool_psutil](https://pypi.org/project/swarmauri_tool_psutil/)
- [swarmauri_tool_qrcodegenerator](https://pypi.org/project/swarmauri_tool_qrcodegenerator/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Zapier Webhooks documentation](https://zapier.com/apps/webhook/help)
- [HTTPX documentation](https://www.python-httpx.org/)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Treat the Zapier hook URL as a secret.
- Validate payload structure before shipping high-value events.
- Wrap calls with retries or circuit breakers if delivery reliability matters.
- Extend the tool if your Zap requires headers, timeouts, or a different JSON
  envelope.

## License

This project is licensed under the Apache-2.0 License.
