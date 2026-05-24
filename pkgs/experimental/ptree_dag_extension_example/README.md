![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/ptree_dag_extension_example/">
        <img src="https://static.pepy.tech/badge/ptree_dag_extension_example/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/ptree_dag_extension_example/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/ptree_dag_extension_example.svg"/></a>
    <a href="https://pypi.org/project/ptree_dag_extension_example/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/ptree_dag_extension_example/">
        <img src="https://img.shields.io/pypi/l/ptree_dag_extension_example" alt="License"/></a>
    <a href="https://pypi.org/project/ptree_dag_extension_example/">
        <img src="https://img.shields.io/pypi/v/ptree_dag_extension_example?label=ptree_dag_extension_example&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Ptree Dag Extension Example

Swarmauri's Ptree Dag.

## Features

- Swarmauri's Ptree Dag.
- Keeps the package surface isolated so you can install only the capability you need instead of the full workspace.
- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add ptree_dag_extension_example
```

```bash
pip install ptree_dag_extension_example
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
import ptree_dag.templates

print(ptree_dag.templates.__name__)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
