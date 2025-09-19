![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_containerfeedchars/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_containerfeedchars" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containerfeedchars/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containerfeedchars.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containerfeedchars/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_containerfeedchars" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containerfeedchars/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_containerfeedchars" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containerfeedchars/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_containerfeedchars?label=swarmauri_tool_containerfeedchars&color=green" alt="PyPI - swarmauri_tool_containerfeedchars"/></a>
</p>

---

# Swarmauri Tool ContainerFeedChars

Execute commands inside a Docker or Kubernetes container session.

## Installation

```bash
pip install swarmauri_tool_containerfeedchars
```

## Usage

```python
from swarmauri_tool_containerfeedchars import ContainerFeedCharsTool

tool = ContainerFeedCharsTool(container_name="my-container")
output = tool(command="ls -al")
print(output["stdout"])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.