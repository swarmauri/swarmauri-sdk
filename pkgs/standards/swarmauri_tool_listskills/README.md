# ListSkills

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_listskills)](https://pepy.tech/projects/swarmauri_tool_listskills)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_listskills.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_listskills)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_listskills)](https://pypi.org/project/swarmauri_tool_listskills/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_listskills)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_listskills?label=swarmauri_tool_listskills&color=green)](https://pypi.org/project/swarmauri_tool_listskills/)

List available skills.

## Features

- List available skills.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_listskills
pip install swarmauri_tool_listskills
```

## Usage

```python
from swarmauri_tool_listskills import ListSkills

def make_tool(catalog):
    return ListSkills(catalog=catalog)
```
