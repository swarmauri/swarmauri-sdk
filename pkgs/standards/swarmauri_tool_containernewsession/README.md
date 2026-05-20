![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_containernewsession/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_containernewsession/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containernewsession/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_containernewsession.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_containernewsession/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
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
