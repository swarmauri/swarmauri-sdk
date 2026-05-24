![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swm_example_plugin/">
        <img src="https://static.pepy.tech/badge/swm_example_plugin/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/example_plugin/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/example_plugin.svg"/></a>
    <a href="https://pypi.org/project/swm_example_plugin/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swm_example_plugin/">
        <img src="https://img.shields.io/pypi/l/swm_example_plugin" alt="License"/></a>
    <a href="https://pypi.org/project/swm_example_plugin/">
        <img src="https://img.shields.io/pypi/v/swm_example_plugin?label=swm_example_plugin&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swm Example Plugin

This repository includes an example of a Swarmauri Plugin.

## Features

- This repository includes an example of a Swarmauri Plugin.
- Exposes discoverable runtime entry points for `swarmauri.plugins` so the package can be wired into Swarmauri or Tigrbl workflows.
- Supports direct plugin instantiation from application code; avoid `PluginManager` unless a task explicitly requires it.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swm_example_plugin
```

```bash
pip install swm_example_plugin
```

## Usage

Instantiate the exported plugin classes directly in your application or test harness. Do not route plugin setup through `PluginManager` unless you were explicitly asked to do so.

```python
from swm_example_plugin import Path

exports = ['Path']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
