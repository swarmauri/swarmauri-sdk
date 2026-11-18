![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_taskstore_sqlite

[![Downloads](https://static.pepy.tech/badge/swarmauri_taskstore_sqlite/month)](https://pepy.tech/project/swarmauri_taskstore_sqlite)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_taskstore_sqlite.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_taskstore_sqlite)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_taskstore_sqlite)
[![License](https://img.shields.io/pypi/l/swarmauri_taskstore_sqlite)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_taskstore_sqlite)](https://pypi.org/project/swarmauri_taskstore_sqlite)

Interchangeable task stores component for the composable execution framework.

## Features

- Export `SqliteTaskStore` with SDK interface/base-class inheritance and entry-point discovery.
- Keep user authority, workload identity, lifecycle and delivery dependencies explicit.
- Reuse existing service registries, transports, checkpoints and token providers.
- Support Python 3.10, 3.11 and 3.12.

## Installation

These packages introduce unreleased core/base APIs. Install the matching workspace revision together; do not combine with older published core/base releases. Release validation must publish compatible dependency versions first.

```sh
uv pip install ./pkgs/standards/swarmauri_taskstore_sqlite
pip install ./pkgs/standards/swarmauri_taskstore_sqlite
```

## Usage

The following is composition code. Injected dependency names are host configuration, not bundled mock providers. Async statements run inside an async function.

```python
import time
from swarmauri_core.permissions import Permission
from swarmauri_core.tasks import TaskRecord
from swarmauri_taskstore_sqlite import SqliteTaskStore

store = SqliteTaskStore(path="tasks.db")
store.create(TaskRecord(
    "report-1", "user:alice", "acme",
    (Permission("documents:read", "document:123", "acme"),),
    int(time.time()) + 600,
))
assert store.load("report-1").subject == "user:alice"
```

See [the complete architecture and deployment guide](../../../docs/examples/composable-execution/README.md) for concrete local commands, live OIDC integration, HTTP hosting, lifecycle semantics and failure recovery.

## Verification

From `pkgs/`, with the workspace dependencies installed:

```sh
uv run --package swarmauri_taskstore_sqlite --directory standards/swarmauri_taskstore_sqlite pytest
uv run --package swarmauri_taskstore_sqlite --directory standards/swarmauri_taskstore_sqlite ruff check .
```

Tests use real signing and stores where applicable; scripted models are explicitly identified fixtures. No live provider interoperability is claimed by offline tests.

## Contributing

Follow the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/AGENTS.md).
