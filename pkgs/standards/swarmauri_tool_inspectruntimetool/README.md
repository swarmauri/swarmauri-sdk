# InspectRuntimeTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_inspectruntimetool)](https://pepy.tech/projects/swarmauri_tool_inspectruntimetool)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_inspectruntimetool.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_inspectruntimetool)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_inspectruntimetool)](https://pypi.org/project/swarmauri_tool_inspectruntimetool/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_inspectruntimetool)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_inspectruntimetool?label=swarmauri_tool_inspectruntimetool&color=green)](https://pypi.org/project/swarmauri_tool_inspectruntimetool/)

Inspect a runtime tool and its declared inputs.

## Features

- Inspect a runtime tool and its declared inputs.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_inspectruntimetool
pip install swarmauri_tool_inspectruntimetool
```

## Usage

```python
from swarmauri_tool_inspectruntimetool import InspectRuntimeTool

def make_tool(toolkit):
    return InspectRuntimeTool(toolkit=toolkit)
```
