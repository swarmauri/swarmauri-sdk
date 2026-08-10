![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_storage_webdav/">
        <img src="https://static.pepy.tech/badge/swarmauri_storage_webdav/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_webdav/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_webdav.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_webdav/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_webdav/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_webdav" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_webdav/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_webdav?label=swarmauri_storage_webdav&color=green" alt="Release Version"/></a>
</p>

# Swarmauri Storage WebDAV

A WebDAV client storage adapter for SwarmauriSDK workflows that store files
and directory trees in remote DAV collections.

## Features

- Implements the Swarmauri storage adapter upload, download, push, pull,
  range-read, byte, and removal workflows.
- Creates remote collections with `MKCOL` and enumerates directory trees with
  bounded `PROPFIND Depth: 1` requests.
- Provides capability discovery through `OPTIONS` and server-side `COPY` and
  `MOVE` extensions.
- Supports Basic, Bearer, custom `httpx.Auth`, TLS verification, and mutual TLS
  client configuration.
- Normalizes logical keys, percent-encodes URL path segments, rejects path
  traversal, and rejects DTD/entity declarations before parsing multistatus
  XML.
- Provides discoverable `swarmauri.storage_adapters` and
  `peagen.plugins.storage_adapters` entry points.

`LOCK` and `UNLOCK` are not exposed. Their presence alone does not establish
complete DAV class-2 behavior; lock-token ownership, refresh, timeout, and
conditional-write semantics require a dedicated contract.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_storage_webdav
```

```bash
pip install swarmauri_storage_webdav
```

## Usage

Create an adapter for an existing WebDAV collection and optionally scope all
keys beneath a prefix.

```python
from swarmauri_storage_webdav import WebDAVStorageAdapter

with WebDAVStorageAdapter(
    base_url="https://dav.example.com/remote.php/dav/files/jacob/",
    username="jacob",
    password="secret",
    prefix="artifacts",
) as storage:
    storage.put_blob("runs/42/result.json", b'{"status":"complete"}')
    payload = storage.get_blob("runs/42/result.json")

    storage.push("./dist", prefix="releases/0.1.0")
    storage.pull("releases/0.1.0", "./download")

    print(storage.capabilities())
    print(payload)
```

URI construction is also supported. Credentials are removed from the stored
HTTP endpoint and must not be logged.

```python
storage = WebDAVStorageAdapter.from_uri(
    "webdav+https://jacob:secret@dav.example.com/files/jacob/"
)
```

The endpoint root must already exist. `ensure_bucket()` creates the configured
prefix when one is present; without a prefix it validates the endpoint through
`OPTIONS`.

License: Apache-2.0. See `LICENSE`.
