![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_containermakepr/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_containermakepr" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containermakepr/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containermakepr.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containermakepr/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_containermakepr" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containermakepr/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_containermakepr" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containermakepr/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_containermakepr?label=swarmauri_tool_containermakepr&color=green" alt="PyPI - swarmauri_tool_containermakepr"/></a>
</p>

---

# Swarmauri Tool ContainerMakePR

Create GitHub pull requests from within a container using the `gh` CLI.

## Installation

```bash
pip install swarmauri_tool_containermakepr
```

## Usage

```python
from swarmauri_tool_containermakepr import ContainerMakePrTool

tool = ContainerMakePrTool(container_name="my-container")
tool(title="Update", body="PR body")
```
