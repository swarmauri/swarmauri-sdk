![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_stdio/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_stdio/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_stdio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_stdio.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_stdio/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_stdio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_stdio" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_stdio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_stdio?label=swarmauri_transport_stdio&color=green" alt="PyPI - swarmauri_transport_stdio"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Transport ? STDIO Bridge

`swarmauri-transport-stdio` spawns subprocesses and communicates over standard input/output so command-line tools can act as Swarmauri peers.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-stdio --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-stdio
```

## Usage

```python
import asyncio
from swarmauri_transport_stdio import StdioTransport

async def run_tool() -> None:
    transport = StdioTransport(["python", "script.py"])
    async with transport.client():
        await transport.send("tool", b"input\n")
        print(await transport.recv())

asyncio.run(run_tool())
```

Wrap any CLI-friendly model or service and adapt its IO using the Swarmauri transport interfaces.


