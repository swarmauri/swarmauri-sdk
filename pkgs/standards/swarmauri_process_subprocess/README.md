# SubprocessBackend

![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_process_subprocess)](https://pepy.tech/projects/swarmauri_process_subprocess)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_process_subprocess.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_process_subprocess)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_process_subprocess)](https://pypi.org/project/swarmauri_process_subprocess/)
[![License](https://img.shields.io/pypi/l/swarmauri_process_subprocess)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_process_subprocess?label=swarmauri_process_subprocess&color=green)](https://pypi.org/project/swarmauri_process_subprocess/)

Stream and control commands running on the local host.

## Features

- Stream and control commands running on the local host.
- Supports Python 3.10 through 3.12.

## Installation

```sh
uv add swarmauri_process_subprocess
pip install swarmauri_process_subprocess
```

## Usage

```python
from swarmauri_core.processes import ProcessRequest
from swarmauri_process_subprocess import SubprocessBackend

backend = SubprocessBackend()
handle = backend.start(ProcessRequest(("python", "--version")))
cursor = 0
while True:
    page = backend.read(handle, after=cursor, wait=1)
    cursor = page.cursor
    for event in page.events:
        print(event.kind, event.data, event.exit_code)
    if page.events and page.events[-1].kind == "exit":
        break
backend.release(handle)
```
