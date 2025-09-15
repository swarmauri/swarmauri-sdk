![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_toolkit_containertoolkit" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_containertoolkit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_containertoolkit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_toolkit_containertoolkit" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_containertoolkit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_containertoolkit?label=swarmauri_toolkit_containertoolkit&color=green" alt="PyPI - swarmauri_toolkit_containertoolkit"/></a>
</p>

---

# Swarmauri Toolkit ContainerToolkit

An aggregation of container management tools for Swarmauri agents.

## Installation

```bash
pip install swarmauri_toolkit_containertoolkit
```

## Usage

```python
from swarmauri_toolkit_containertoolkit import ContainerToolkit

toolkit = ContainerToolkit(container_name="my-container", image="ubuntu:latest")
print(toolkit.tools.keys())
```
