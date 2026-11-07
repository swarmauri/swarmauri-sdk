![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_findfile/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_findfile" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_findfile/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_findfile.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_findfile/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_findfile" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_findfile/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_findfile" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_findfile/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_findfile?label=swarmauri_tool_findfile&color=green" alt="PyPI - swarmauri_tool_findfile"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Find File

`swarmauri_tool_findfile` searches a directory for files whose name matches a
shell-style wildcard, case-insensitively, with optional recursion into
subdirectories.

## Features

- **Wildcard matching** with `*`, `?` and `[seq]`, matched against the file
  name rather than the whole path.
- **Case-insensitive** on every platform, so `*.LOG` and `*.log` behave the
  same wherever the code runs.
- **Optional recursion** via `recursive=True`; the default checks one level.
- **Never follows symbolic links**, so a link cycle cannot make the walk run
  forever.
- **Returns files, not directories.** This answers "which files match", not
  "what is here".
- **Reports problems instead of raising**, with the same result shape in every
  case.

## Installation

```bash
# With uv
uv add swarmauri_tool_findfile

# With pip
pip install swarmauri_tool_findfile
```

## Usage

```python
from pathlib import Path

from swarmauri_tool_findfile import FindFileTool

# Build a small tree so the example is reproducible.
Path("/tmp/logs/archive").mkdir(parents=True, exist_ok=True)
Path("/tmp/logs/app.log").write_text("x", encoding="utf-8")
Path("/tmp/logs/archive/old.log").write_text("x", encoding="utf-8")

tool = FindFileTool(allowed_roots=["/tmp/logs"])

tool(path="/tmp/logs", pattern="*.log")
# {"path": "/tmp/logs", "pattern": "*.log", "count": 1,
#  "matches": ["/tmp/logs/app.log"]}

tool(path="/tmp/logs", pattern="*.log", recursive=True)
# {"count": 2, "matches": ["/tmp/logs/app.log", "/tmp/logs/archive/old.log"]}
```

### Result keys

| Key | Type | Meaning |
| --- | --- | --- |
| `path` | `str` | Root directory that was searched |
| `pattern` | `str` | Pattern as supplied |
| `count` | `int` | Number of matching files |
| `matches` | `list[str]` | Absolute paths, sorted |
| `error` | `str` | Present only when the search could not run |

## Expected workflows

- **Locate by extension.** `*.csv` before loading a dataset.
- **Find a report by convention.** `report?.txt` or `2026-*.pdf`.
- **Scope a bulk action.** Gather matches, then act on the list.

## FAQ

> **Why case-insensitive by default rather than by flag?**  
> The same tree yields different results on macOS and Linux otherwise, and a
> search that silently misses `Report.PDF` is the failure mode that hurts.

> **Does it follow symlinks?**  
> No. Links are never traversed, so a directory that links back to its parent
> cannot produce an infinite walk.

> **Why does it only return files?**  
> Directories are a different question with a different tool; mixing them makes
> every caller filter the result.


## Trusted roots and resource limits

Configure `allowed_roots` on the tool from trusted service code. The default is
its construction-time working directory. Relative requests use the call-time
working directory and must still lie beneath a configured root. Empty roots
reject every request. Roots must be absolute; parent traversal and symlinks in
requested directory paths or root paths are rejected.

Where Linux `openat2` is available, lookups use beneath-root resolution.
If the syscall is unavailable, the POSIX fallback opens a single child of
the trusted root with a no-follow lookup. Nested directory lookups fail
with `ENOTSUP`. Policy denials such as `EPERM` or `EACCES` are returned as
errors, including when opening the configured root. Searching from the configured root
or a direct child is supported as long as the search need not open a
directory more than one level below the configured root. A search that
needs to open a deeper directory returns an error and discards partial
results.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

On POSIX, recursive directories are opened from the original root handle and
checked again by identity after enumeration. A detected move or replacement causes the scan to fail.

Service-owned defaults cap scans at 100,000 entries, results at 10,000, returned
JSON at 1 MiB, and elapsed scanning at two seconds. These constructor fields
(`max_scanned_entries`, `max_results`, `max_return_bytes`,
`max_elapsed_seconds`) are not agent-call parameters. Limit exhaustion returns
an explicit error and an empty result rather than successful partial data.
Time checks are cooperative and cannot interrupt a filesystem call blocked in
the kernel. Success responses obey `max_return_bytes`. Error responses truncate
echoed input and diagnostics to at most 4 KiB, or the configured byte budget
when smaller, with a 256-byte minimum to preserve a structured error envelope.

Both search modes return regular files only: symlinks, FIFOs, sockets, and other
special entries are excluded. Recursive directory opens are descriptor-relative
and never follow symlinks. `max_depth` defaults to 64 and
`max_pattern_length` to 1,024 characters; both are service-owned limits. Filename
matching remains case-insensitive, and results remain sorted absolute paths.

### Windows filesystem support

On Windows the backend opens the local drive by its volume identity and
opens each component relative to a held directory handle. It rejects junctions
and other reparse points and does not accept UNC or device paths, alternate data
streams, or ambiguous trailing dots or spaces, or reserved DOS basenames. Ancestors are
opened for traversal. Only a directory being enumerated requires listing access.
Volume and directory handles
deny delete sharing during traversal. Returned paths are descriptive snapshots.
Entries with names that ordinary Windows paths cannot represent are omitted.
A listed pathname conveys no permission to open its contents.
