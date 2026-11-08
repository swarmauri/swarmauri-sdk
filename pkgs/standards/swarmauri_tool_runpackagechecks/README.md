# RunPackageChecks

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_runpackagechecks)](https://pepy.tech/projects/swarmauri_tool_runpackagechecks)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_runpackagechecks.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_runpackagechecks)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tool_runpackagechecks)](https://pypi.org/project/swarmauri_tool_runpackagechecks/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_runpackagechecks)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_runpackagechecks?label=swarmauri_tool_runpackagechecks&color=green)](https://pypi.org/project/swarmauri_tool_runpackagechecks/)

Run the SDK Ruff and pytest checks for a configured member.

## Features

- Run the SDK Ruff and pytest checks for a configured member.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_tool_runpackagechecks
pip install swarmauri_tool_runpackagechecks
```

## Usage

```python
from swarmauri_tool_runpackagechecks import RunPackageChecks

def checks_tool(backend):
    return RunPackageChecks(backend=backend, members={"swarmauri_core": "pkgs/core"})
```
