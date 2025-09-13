<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
