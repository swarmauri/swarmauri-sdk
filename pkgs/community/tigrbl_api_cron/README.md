![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_api_cron/">
        <img src="https://static.pepy.tech/badge/tigrbl_api_cron/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/tigrbl_api_cron/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/tigrbl_api_cron.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/pypi/l/tigrbl_api_cron" alt="License"/></a>
    <a href="https://pypi.org/project/tigrbl_api_cron/">
        <img src="https://img.shields.io/pypi/v/tigrbl_api_cron?label=tigrbl_api_cron&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Tigrbl API Cron

Cron job storage, execution, and result tracking built on the Tigrbl engine.

## Features

- Cron job storage, execution, and result tracking built on the Tigrbl engine.
- Centers its public API around `app`, `build_app`, `execute_due_jobs`, `CronJobHandler` so downstream code can import the package directly without extra registry glue.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add tigrbl_api_cron
```

```bash
pip install tigrbl_api_cron
```

## Usage

Import the exported types and wire them into the Tigrbl application or runtime where this package is needed.

```python
from tigrbl_api_cron import app, build_app, execute_due_jobs, CronJobHandler

exports = ['app', 'build_app', 'execute_due_jobs', 'CronJobHandler']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
