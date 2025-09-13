<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
