# ListRuntimeTools

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_listruntimetools)](https://pepy.tech/projects/swarmauri_tool_listruntimetools)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_listruntimetools.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_listruntimetools)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_listruntimetools)](https://pypi.org/project/swarmauri_tool_listruntimetools/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_listruntimetools)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_listruntimetools?label=swarmauri_tool_listruntimetools&color=green)](https://pypi.org/project/swarmauri_tool_listruntimetools/)

List the tools in a runtime toolkit.

## Features

- List the tools in a runtime toolkit.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_listruntimetools
pip install swarmauri_tool_listruntimetools
```

## Usage

```python
from swarmauri_tool_listruntimetools import ListRuntimeTools

def make_tool(toolkit):
    return ListRuntimeTools(toolkit=toolkit)
```
