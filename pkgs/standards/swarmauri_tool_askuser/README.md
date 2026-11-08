# AskUserTool

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_askuser)](https://pepy.tech/projects/swarmauri_tool_askuser)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_askuser.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_askuser)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_askuser)](https://pypi.org/project/swarmauri_tool_askuser/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_askuser)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_askuser?label=swarmauri_tool_askuser&color=green)](https://pypi.org/project/swarmauri_tool_askuser/)

Collect validated human input through an application-provided handler.

## Features

- Collect validated human input through an application-provided handler.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_askuser
pip install swarmauri_tool_askuser
```

## Usage

```python
from swarmauri_tool_askuser import AskUserTool

ask = AskUserTool(input_handler=lambda question: input(question.content + " "))
answer = ask("Which package?", choices=["core", "base"])
print(answer.answer)
```
