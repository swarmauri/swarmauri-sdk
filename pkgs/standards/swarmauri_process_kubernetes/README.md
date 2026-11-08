# KubernetesProcessBackend

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_process_kubernetes)](https://pepy.tech/projects/swarmauri_process_kubernetes)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_process_kubernetes.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_process_kubernetes)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_process_kubernetes)](https://pypi.org/project/swarmauri_process_kubernetes/)
[![License](https://img.shields.io/pypi/l/swarmauri_process_kubernetes)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_process_kubernetes?label=swarmauri_process_kubernetes&color=green)](https://pypi.org/project/swarmauri_process_kubernetes/)

Stream and control processes in a kubernetes workspace with Python 3 installed.

## Features

- Stream and control processes in a kubernetes workspace with Python 3 installed.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_process_kubernetes
pip install swarmauri_process_kubernetes
```

## Usage

```python
from swarmauri_core.processes import ProcessRequest
from swarmauri_process_kubernetes import KubernetesProcessBackend

backend = KubernetesProcessBackend()
# The target workspace must already exist and include Python 3.
handle = backend.start(ProcessRequest(("python3", "--version"), workspace="sdk-checks"))
print(backend.read(handle, wait=1))
```
