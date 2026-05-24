![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_entityrecognition/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_entityrecognition/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_entityrecognition/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_entityrecognition.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_entityrecognition" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_entityrecognition/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_entityrecognition?label=swarmauri_parser_entityrecognition&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Parser Entityrecognition

spaCy-based named-entity recognition parser for Swarmauri with structured entity document output.

## Features

- spaCy-based named-entity recognition parser for Swarmauri with structured entity document output.
- Exposes discoverable runtime entry points for `swarmauri.parsers` so the package can be wired into Swarmauri or Tigrbl workflows.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_parser_entityrecognition
```

```bash
pip install swarmauri_parser_entityrecognition
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

exports = ['EntityRecognitionParser']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
