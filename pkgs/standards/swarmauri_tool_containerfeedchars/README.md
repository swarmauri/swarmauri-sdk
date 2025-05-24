![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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
