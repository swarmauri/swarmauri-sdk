![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_entityrecognition/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_entityrecognition/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_entityrecognition/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_entityrecognition.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_entityrecognition" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_entityrecognition?label=swarmauri_tool_entityrecognition&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Tool Entityrecognition

Transformer-based named-entity recognition tool for Swarmauri with JSON-serialized grouped entity output.

## Features

- Transformer-based named-entity recognition tool for Swarmauri with JSON-serialized grouped entity output.
- Exposes discoverable runtime entry points for `swarmauri.tools` so the package can be wired into Swarmauri or Tigrbl workflows.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_tool_entityrecognition
```

```bash
pip install swarmauri_tool_entityrecognition
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_tool_entityrecognition import EntityRecognitionTool

exports = ['EntityRecognitionTool']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
