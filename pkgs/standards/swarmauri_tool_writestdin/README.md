# WriteStdinTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_writestdin)](https://pepy.tech/projects/swarmauri_tool_writestdin)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_writestdin.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_writestdin)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_writestdin)](https://pypi.org/project/swarmauri_tool_writestdin/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_writestdin)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_writestdin?label=swarmauri_tool_writestdin&color=green)](https://pypi.org/project/swarmauri_tool_writestdin/)

Write text to an existing process or close its input.

## Features

- Write text to an existing process or close its input.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_writestdin
pip install swarmauri_tool_writestdin
```

## Usage

```python
from swarmauri_tool_writestdin import WriteStdinTool

# Supply the backend that owns the process session.
def make_tool(backend):
    return WriteStdinTool(backend=backend)
```
