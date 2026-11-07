# CancelProcessTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_cancelprocess)](https://pepy.tech/projects/swarmauri_tool_cancelprocess)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_cancelprocess.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_cancelprocess)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_cancelprocess)](https://pypi.org/project/swarmauri_tool_cancelprocess/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_cancelprocess)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_cancelprocess?label=swarmauri_tool_cancelprocess&color=green)](https://pypi.org/project/swarmauri_tool_cancelprocess/)

Cancel a running process by handle.

## Features

- Cancel a running process by handle.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_cancelprocess
pip install swarmauri_tool_cancelprocess
```

## Usage

```python
from swarmauri_tool_cancelprocess import CancelProcessTool

# Supply the backend that owns the process session.
def make_tool(backend):
    return CancelProcessTool(backend=backend)
```
