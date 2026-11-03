![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_listfiles/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_listfiles/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_listfiles/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_listfiles.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_listfiles/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_listfiles/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_listfiles" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_listfiles/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_listfiles?label=swarmauri_tool_listfiles&color=green" alt="PyPI - swarmauri_tool_listfiles"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool List Files

`swarmauri_tool_listfiles` lists what is directly inside a folder: files and
directories, sorted by name, with an optional absolute path for each entry. It
does not recurse, so a listing stays cheap no matter how deep the tree is.

## Features

- **Lists files and directories** in a single call, sorted case-insensitively.
- **Marks directories** with `is_dir`, so a caller never has to guess.
- **Optional absolute paths** via `full_paths=True`; names only by default.
- **Does not recurse.** Deep trees cannot turn a listing into a full scan.
- **Reports problems instead of raising.** A missing path, a path that is a
  file, and an unreadable directory all come back as a structured result.
- **Expands `~`** so home-relative paths work without extra handling.

## Installation

```bash
# With uv
uv add swarmauri_tool_listfiles

# With pip
pip install swarmauri_tool_listfiles
```

## Usage

```python
from pathlib import Path

from swarmauri_tool_listfiles import ListFilesTool

# Use a directory that exists; the tool lists what is there and does not
# create anything.
Path("/tmp/project").mkdir(parents=True, exist_ok=True)
Path("/tmp/project/README.md").write_text("x", encoding="utf-8")
Path("/tmp/project/src").mkdir(exist_ok=True)

tool = ListFilesTool()

result = tool(path="/tmp/project")
# {
#   "path": "/tmp/project",
#   "count": 2,
#   "entries": [
#     {"name": "README.md", "is_dir": False},
#     {"name": "src", "is_dir": True},
#   ],
# }

result = tool(path="/tmp/project", full_paths=True)
# {"name": "README.md", "is_dir": False, "path": "/tmp/project/README.md"}
```

### Result keys

| Key | Type | Meaning |
| --- | --- | --- |
| `path` | `str` | Resolved directory that was listed |
| `count` | `int` | Number of entries |
| `entries` | `list` | `{"name", "is_dir"}`, plus `"path"` when `full_paths` is set |
| `error` | `str` | Present only when the directory could not be listed |

## Expected workflows

- **Survey before acting.** An agent lists a folder, then chooses a file to
  read or edit.
- **Confirm a write target.** List the parent directory to check that a name is
  free before creating a file.
- **Fail safely.** Callers check for `error` rather than wrapping the call in
  `try`, because refusals are values, not exceptions.

## FAQ

> **Does it recurse?**  
> No. Use a search tool for that. A listing of a huge tree stays a listing of
> one level.

> **Why sort by name rather than directories first?**  
> A stable, predictable order matters more than grouping; callers that care
> filter on `is_dir`.

> **Are symlinks followed?**  
> Entries are listed as they appear. A symlink to a directory reports
> `is_dir: True` and is not traversed, because nothing is traversed.
