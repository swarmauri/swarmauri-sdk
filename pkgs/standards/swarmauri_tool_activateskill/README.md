# ActivateSkill

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_activateskill)](https://pepy.tech/projects/swarmauri_tool_activateskill)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_activateskill.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_activateskill)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_activateskill)](https://pypi.org/project/swarmauri_tool_activateskill/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_activateskill)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_activateskill?label=swarmauri_tool_activateskill&color=green)](https://pypi.org/project/swarmauri_tool_activateskill/)

Load a skill and expose its approved tools.

## Features

- Load a skill and expose its approved tools.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_activateskill
pip install swarmauri_tool_activateskill
```

## Usage

```python
from swarmauri_tool_activateskill import ActivateSkill

def make_tool(catalog):
    return ActivateSkill(catalog=catalog)
```
