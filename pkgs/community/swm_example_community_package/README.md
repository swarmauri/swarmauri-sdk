![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swm_example_community_package/">
        <img src="https://static.pepy.tech/badge/swm_example_community_package/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swm_example_community_package/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swm_example_community_package.svg"/></a>
    <a href="https://pypi.org/project/swm_example_community_package/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swm_example_community_package/">
        <img src="https://img.shields.io/pypi/l/swm_example_community_package" alt="License"/></a>
    <a href="https://pypi.org/project/swm_example_community_package/">
        <img src="https://img.shields.io/pypi/v/swm_example_community_package?label=swm_example_community_package&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swm Example Community Package

example community package.

## Features

- example community package.
- Exposes discoverable runtime entry points for `swarmauri.agents` so the package can be wired into Swarmauri or Tigrbl workflows.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swm_example_community_package
```

```bash
pip install swm_example_community_package
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swm_example_community_package import PackageNotFoundError, version, Path

exports = ['PackageNotFoundError', 'version', 'Path']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
