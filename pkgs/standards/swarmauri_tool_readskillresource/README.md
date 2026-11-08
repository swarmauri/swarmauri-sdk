# ReadSkillResource

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_readskillresource)](https://pepy.tech/projects/swarmauri_tool_readskillresource)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_readskillresource.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_readskillresource)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_readskillresource)](https://pypi.org/project/swarmauri_tool_readskillresource/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_readskillresource)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_readskillresource?label=swarmauri_tool_readskillresource&color=green)](https://pypi.org/project/swarmauri_tool_readskillresource/)

Read a declared skill resource.

## Features

- Read a declared skill resource.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_readskillresource
pip install swarmauri_tool_readskillresource
```

## Usage

```python
from swarmauri_tool_readskillresource import ReadSkillResource

def make_tool(catalog):
    return ReadSkillResource(catalog=catalog)
```
