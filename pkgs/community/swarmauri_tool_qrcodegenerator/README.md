![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

# Swarmauri Tool · QR Code Generator

A Swarmauri tool that converts text payloads into QR codes and returns the image data as a Base64 string. Plug it into conversational agents, marketing workflows, or automation scripts that need scannable hand-offs (URLs, Wi-Fi credentials, one-time tokens, etc.).

- Backed by `qrcode`/Pillow to produce standards-compliant QR codes.
- Outputs Base64 so responses can be embedded directly in JSON, HTML, or rich chat messages.
- Exposed through the standard Swarmauri tool interface for drop-in registration alongside other capabilities.

## Requirements

- Python 3.10 – 3.13.
- `qrcode` (installs with its Pillow dependency) and Swarmauri base packages (`swarmauri_base`, `swarmauri_standard`, `pydantic`).
- Optional: downstream consumers often decode the Base64 string using Pillow or write it to disk; ensure those environments can handle binary data.

## Installation

Choose the tooling that matches your project; each command resolves transitive dependencies.

**pip**

```bash
pip install swarmauri_tool_qrcodegenerator
```

**Poetry**

```bash
poetry add swarmauri_tool_qrcodegenerator
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_qrcodegenerator

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_qrcodegenerator
```

> Tip: Pillow requires native image libraries on some Linux distributions (e.g., `libjpeg`, `zlib`). Install OS packages before running the commands above in minimal containers.

## Quick Start

```python
import base64
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

qr_tool = QrCodeGeneratorTool()
result = qr_tool("https://docs.swarmauri.ai")

image_b64 = result["image_b64"]
with open("docs-qrcode.png", "wb") as f:
    f.write(base64.b64decode(image_b64))
```

The output image uses the tool's default QR code settings (`version=1`, low error correction, black modules on white background). Adjust presentation after decoding if you need different colors or scaling.

## Usage Scenarios

### Embed QR Codes in Agent Responses

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

registry = ToolRegistry()
registry.register(QrCodeGeneratorTool())
agent = Agent(tool_registry=registry)

message = HumanMessage(content="Create a QR code for https://status.mycompany.com")
response = agent.run(message)
print(response)
```

Agents can attach the Base64 image to chat payloads so end users scan the code without additional steps.

### Publish Dynamic Event Badges

```python
import base64
from pathlib import Path
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

qr_tool = QrCodeGeneratorTool()
attendees = {
    "alice": "ticket:EVT-001-A1B2",
    "bob": "ticket:EVT-002-B3C4",
}

badges_dir = Path("badges")
badges_dir.mkdir(exist_ok=True)

for name, token in attendees.items():
    b64_img = qr_tool(token)["image_b64"]
    (badges_dir / f"{name}.png").write_bytes(base64.b64decode(b64_img))
```

Generate per-attendee QR codes that scanners can translate into ticket tokens at check-in.

### Serve Codes Over HTTP

```python
import base64
from fastapi import FastAPI, Response
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

app = FastAPI()
qr_tool = QrCodeGeneratorTool()

@app.get("/qr")
def qr_endpoint(data: str):
    result = qr_tool(data)
    png_bytes = base64.b64decode(result["image_b64"])
    return Response(content=png_bytes, media_type="image/png")
```

Expose an API that transforms arbitrary data into QR codes your front-end can display.

## Troubleshooting

- **Blank or unreadable codes** – Confirm the Base64 string is decoded to a PNG (`base64.b64decode(...)`). Avoid writing the raw Base64 text directly to file.
- **Binary dependency errors (Pillow)** – Install platform-specific libraries (`apt-get install libjpeg-dev zlib1g-dev`, etc.) before installing the package, especially in slim containers.
- **Large payloads** – Version 1 QR codes have size constraints (~17 alphanumeric characters). Fork the tool or extend it to allow larger versions if you need to encode lengthy data.

## License

`swarmauri_tool_qrcodegenerator` is released under the Apache 2.0 License. See `LICENSE` for details.
