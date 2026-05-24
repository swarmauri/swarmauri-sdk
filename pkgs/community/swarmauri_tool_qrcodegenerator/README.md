![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_qrcodegenerator/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_qrcodegenerator/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_qrcodegenerator.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_qrcodegenerator" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_qrcodegenerator/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_qrcodegenerator?label=swarmauri_tool_qrcodegenerator&color=green" alt="PyPI - swarmauri_tool_qrcodegenerator"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool QR Code Generator

`swarmauri_tool_qrcodegenerator` is a Swarmauri utility tool for generating QR
codes from text payloads and returning the resulting image bytes as a
base64-encoded string. It is useful for links, identifiers, tickets, device
pairing flows, and automation pipelines that need scannable data artifacts.

## Why Use Swarmauri Tool QR Code Generator

- Turn text values into scannable QR artifacts inside Swarmauri workflows.
- Return image data inline as base64 for transport-friendly downstream use.
- Generate QR content for tickets, links, tokens, or device onboarding.
- Keep QR generation available as a standard Swarmauri tool interface.

## FAQ

> **What input does the tool expect?**  
> A single string `data` value to encode.

> **What does the tool return?**  
> A dictionary with one key: `image_b64`.

> **Does the tool currently write files to disk?**  
> No. It returns encoded image bytes in memory.

> **Can this be used in agent workflows?**  
> Yes. The base64 string can be forwarded to other tools, APIs, or UI layers.

## Features

- Swarmauri `ToolBase` implementation registered as `QrCodeGeneratorTool`.
- Generates QR codes from arbitrary text input.
- Returns base64-encoded image bytes for transport and storage.
- Useful for event, device, credential, and link-sharing workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_qrcodegenerator
```

```bash
pip install swarmauri_tool_qrcodegenerator
```

## Usage

```python
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

tool = QrCodeGeneratorTool()
result = tool("https://docs.swarmauri.com")

print(result["image_b64"][:40])
```

## Examples

### Generate a QR code for a URL

```python
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

tool = QrCodeGeneratorTool()
result = tool("https://example.com")

print(len(result["image_b64"]))
```

### Encode an onboarding token

```python
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

tool = QrCodeGeneratorTool()
token = "device:pairing:ABC123XYZ"
result = tool(token)

print(result.keys())
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

tools = ToolCollection(tools=[QrCodeGeneratorTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_zapierhook](https://pypi.org/project/swarmauri_tool_zapierhook/)
- [swarmauri_tool_webscraping](https://pypi.org/project/swarmauri_tool_webscraping/)
- [swarmauri_tool_downloadpdf](https://pypi.org/project/swarmauri_tool_downloadpdf/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [qrcode package documentation](https://pypi.org/project/qrcode/)
- [Base64 encoding in Python](https://docs.python.org/3/library/base64.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Keep encoded payloads short enough for compact QR generation.
- Validate how your downstream consumer expects to reconstruct the returned
  image bytes.
- Avoid embedding secrets directly unless the QR code lifecycle is controlled.
- Consider extending the tool if you need explicit PNG serialization options.

## License

This project is licensed under the Apache-2.0 License.
