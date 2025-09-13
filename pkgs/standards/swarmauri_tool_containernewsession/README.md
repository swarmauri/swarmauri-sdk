![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_containernewsession/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_containernewsession" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containernewsession/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containernewsession.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containernewsession/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_containernewsession" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containernewsession/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_containernewsession" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containernewsession/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_containernewsession?label=swarmauri_tool_containernewsession&color=green" alt="PyPI - swarmauri_tool_containernewsession"/></a>
</p>

---

# Swarmauri Tool ContainerNewSession

A tool for starting a new Docker or Kubernetes session from your Swarmauri agents.

## Installation

```bash
pip install swarmauri_tool_containernewsession
```

## Usage

```python
from swarmauri_tool_containernewsession import ContainerNewSessionTool

tool = ContainerNewSessionTool(container_name="my-container", image="ubuntu:latest")
result = tool()
print(result["stdout"])
```
