![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://static.pepy.tech/badge/swarmauri_toolkit_containertoolkit/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_containertoolkit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_toolkit_containertoolkit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_containertoolkit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_containertoolkit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_containertoolkit?label=swarmauri_toolkit_containertoolkit&color=green" alt="PyPI - swarmauri_toolkit_containertoolkit"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

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


