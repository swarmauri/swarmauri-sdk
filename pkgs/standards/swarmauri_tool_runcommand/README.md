# RunCommandTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_runcommand)](https://pepy.tech/projects/swarmauri_tool_runcommand)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_runcommand.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_runcommand)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_runcommand)](https://pypi.org/project/swarmauri_tool_runcommand/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_runcommand)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_runcommand?label=swarmauri_tool_runcommand&color=green)](https://pypi.org/project/swarmauri_tool_runcommand/)

Start a command and return its process handle.

## Features

- Start a command and return its process handle.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_runcommand
pip install swarmauri_tool_runcommand
```

## Usage

```python
from swarmauri_tool_runcommand import RunCommandTool

# Supply the backend that owns the process session.
def make_tool(backend):
    return RunCommandTool(backend=backend)
```
