# ReadProcessOutputTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_readprocessoutput)](https://pepy.tech/projects/swarmauri_tool_readprocessoutput)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_readprocessoutput.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_readprocessoutput)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_readprocessoutput)](https://pypi.org/project/swarmauri_tool_readprocessoutput/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_readprocessoutput)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_readprocessoutput?label=swarmauri_tool_readprocessoutput&color=green)](https://pypi.org/project/swarmauri_tool_readprocessoutput/)

Read process output from a continuation cursor.

## Features

- Read process output from a continuation cursor.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_readprocessoutput
pip install swarmauri_tool_readprocessoutput
```

## Usage

```python
from swarmauri_tool_readprocessoutput import ReadProcessOutputTool

# Supply the backend that owns the process session.
def make_tool(backend):
    return ReadProcessOutputTool(backend=backend)
```
