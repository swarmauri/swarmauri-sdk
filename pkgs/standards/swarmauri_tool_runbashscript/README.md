# RunBashScriptTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_runbashscript)](https://pepy.tech/projects/swarmauri_tool_runbashscript)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_runbashscript.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_runbashscript)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_runbashscript)](https://pypi.org/project/swarmauri_tool_runbashscript/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_runbashscript)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_runbashscript?label=swarmauri_tool_runbashscript&color=green)](https://pypi.org/project/swarmauri_tool_runbashscript/)

Start an explicit Bash script and return its process handle.

## Features

- Start an explicit Bash script and return its process handle.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_runbashscript
pip install swarmauri_tool_runbashscript
```

## Usage

```python
from swarmauri_tool_runbashscript import RunBashScriptTool

# Supply the backend that owns the process session.
def make_tool(backend):
    return RunBashScriptTool(backend=backend)
```
