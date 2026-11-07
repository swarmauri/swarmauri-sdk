# RegisterRuntimeTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_registerruntimetool)](https://pepy.tech/projects/swarmauri_tool_registerruntimetool)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_registerruntimetool.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_registerruntimetool)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_registerruntimetool)](https://pypi.org/project/swarmauri_tool_registerruntimetool/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_registerruntimetool)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_registerruntimetool?label=swarmauri_tool_registerruntimetool&color=green)](https://pypi.org/project/swarmauri_tool_registerruntimetool/)

Register a tool in a runtime toolkit.

## Features

- Register a tool in a runtime toolkit.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_registerruntimetool
pip install swarmauri_tool_registerruntimetool
```

## Usage

```python
from swarmauri_tool_registerruntimetool import RegisterRuntimeTool

def make_tool(toolkit):
    return RegisterRuntimeTool(toolkit=toolkit)
```
