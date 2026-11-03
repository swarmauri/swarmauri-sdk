![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_findfile/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_findfile/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_findfile/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_findfile.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_findfile/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="PyPI - Python Version"/></a>
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

tool = FindFileTool()

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
