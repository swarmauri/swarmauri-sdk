# ReplaceRuntimeTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_replaceruntimetool)](https://pepy.tech/projects/swarmauri_tool_replaceruntimetool)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_replaceruntimetool.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_replaceruntimetool)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_replaceruntimetool)](https://pypi.org/project/swarmauri_tool_replaceruntimetool/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_replaceruntimetool)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_replaceruntimetool?label=swarmauri_tool_replaceruntimetool&color=green)](https://pypi.org/project/swarmauri_tool_replaceruntimetool/)

Replace a tool in a runtime toolkit.

## Features

- Replace a tool in a runtime toolkit.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_replaceruntimetool
pip install swarmauri_tool_replaceruntimetool
```

## Usage

```python
from swarmauri_tool_replaceruntimetool import ReplaceRuntimeTool

def make_tool(toolkit):
    return ReplaceRuntimeTool(toolkit=toolkit)
```
