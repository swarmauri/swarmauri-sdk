# Swarmauri SQLite Run Store

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_runstore_sqlite)](https://pepy.tech/projects/swarmauri-runstore-sqlite)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_runstore_sqlite.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_runstore_sqlite)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_runstore_sqlite)](https://pypi.org/project/swarmauri-runstore-sqlite/)
[![License](https://img.shields.io/pypi/l/swarmauri_runstore_sqlite)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_runstore_sqlite?label=swarmauri_runstore_sqlite&color=green)](https://pypi.org/project/swarmauri-runstore-sqlite/)

## Features

- Reopen checkpointed runs from an on-disk SQLite database.
- Save revisions atomically when multiple processes advance a run.
- Read SQLite files created by the original Swarmauri agent runner.

## Installation

```sh
uv add swarmauri-runstore-sqlite
pip install swarmauri-runstore-sqlite
```

## Usage

```python
from swarmauri_core.run_stores import RunCheckpoint
from swarmauri_runstore_sqlite import SqliteRunStore

store = SqliteRunStore(path="runs.db")
store.create(RunCheckpoint("example", 0, '{"status":"ready"}'))
checkpoint = store.load("example")
print(store.save(checkpoint).revision)
```

Pass the store to `AgentRunner` to persist a conversation. Use `runner.load(run_id)`
to read the typed run state.
