![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swamauri_metric_wasserstein/">
        <img src="https://static.pepy.tech/badge/swamauri_metric_wasserstein/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swamauri_metric_wasserstein/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swamauri_metric_wasserstein.svg"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/l/swamauri_metric_wasserstein" alt="License"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/v/swamauri_metric_wasserstein?label=swamauri_metric_wasserstein&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swamauri Metric Wasserstein

Wasserstein metric plugin for Swarmauri vector comparisons.

## Features

- Wasserstein metric plugin for Swarmauri vector comparisons.
- Preserves legacy imports and package boundaries so older integrations can keep running while you migrate to active packages.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swamauri_metric_wasserstein
```

```bash
pip install swamauri_metric_wasserstein
```

## Usage

Use this package only as a compatibility bridge while moving callers onto active packages in the workspace.

```python
from swamauri_metric_wasserstein import WassersteinMetric

exports = ['WassersteinMetric']
print(exports)
```

Expect legacy imports to continue working, but plan migration work because the package is retained for compatibility rather than long-term growth.

License: Apache-2.0. See `LICENSE`.
