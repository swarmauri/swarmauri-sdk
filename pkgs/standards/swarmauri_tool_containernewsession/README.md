<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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
