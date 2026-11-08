# DockerProcessBackend

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_process_docker)](https://pepy.tech/projects/swarmauri_process_docker)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_process_docker.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_process_docker)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_process_docker)](https://pypi.org/project/swarmauri_process_docker/)
[![License](https://img.shields.io/pypi/l/swarmauri_process_docker)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_process_docker?label=swarmauri_process_docker&color=green)](https://pypi.org/project/swarmauri_process_docker/)

Stream and control processes in a docker workspace with Python 3 installed.

## Features

- Stream and control processes in a docker workspace with Python 3 installed.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_process_docker
pip install swarmauri_process_docker
```

## Usage

```python
from swarmauri_core.processes import ProcessRequest
from swarmauri_process_docker import DockerProcessBackend

backend = DockerProcessBackend()
# The target workspace must already exist and include Python 3.
handle = backend.start(ProcessRequest(("python3", "--version"), workspace="sdk-checks"))
print(backend.read(handle, wait=1))
```
