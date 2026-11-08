# InspectSkill

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_inspectskill)](https://pepy.tech/projects/swarmauri_tool_inspectskill)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_inspectskill.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_inspectskill)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_inspectskill)](https://pypi.org/project/swarmauri_tool_inspectskill/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_inspectskill)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_inspectskill?label=swarmauri_tool_inspectskill&color=green)](https://pypi.org/project/swarmauri_tool_inspectskill/)

Inspect metadata for a named skill.

## Features

- Inspect metadata for a named skill.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_inspectskill
pip install swarmauri_tool_inspectskill
```

## Usage

```python
from swarmauri_tool_inspectskill import InspectSkill

def make_tool(catalog):
    return InspectSkill(catalog=catalog)
```
