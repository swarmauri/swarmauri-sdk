![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_documentstore_redis/">
        <img src="https://static.pepy.tech/badge/swarmauri_documentstore_redis/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_documentstore_redis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_documentstore_redis.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/pypi/l/swarmauri_documentstore_redis" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/pypi/v/swarmauri_documentstore_redis?label=swarmauri_documentstore_redis&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Documentstore Redis

Swarmauri Psutil Tool.

## Features

- Swarmauri Psutil Tool.
- Preserves legacy imports and package boundaries so older integrations can keep running while you migrate to active packages.
- Aligns with the current workspace packaging model so the package can participate cleanly in larger Swarmauri SDK builds.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_documentstore_redis
```

```bash
pip install swarmauri_documentstore_redis
```

## Usage

Use this package only as a compatibility bridge while moving callers onto active packages in the workspace.

```python
from swarmauri_documentstore_redis import RedisDocumentStore

exports = ['RedisDocumentStore']
print(exports)
```

Expect legacy imports to continue working, but plan migration work because the package is retained for compatibility rather than long-term growth.

License: Apache-2.0. See `LICENSE`.
