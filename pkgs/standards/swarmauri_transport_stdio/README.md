![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-stdio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-stdio" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_stdio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_stdio.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-stdio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-stdio" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-stdio/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-stdio" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-stdio/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-stdio?label=swarmauri-transport-stdio&color=green" alt="PyPI - swarmauri-transport-stdio"/>
    </a>
</p>

---

# Swarmauri Transport – STDIO Bridge

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
