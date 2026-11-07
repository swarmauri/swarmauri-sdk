![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_listfiles/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_listfiles" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_listfiles/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_listfiles.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_listfiles/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_listfiles" alt="PyPI - Python Version"/></a>
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

tool = ListFilesTool(allowed_roots=["/tmp/project"])

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
> Symlink entries are listed without dereferencing their targets and report
> `is_dir: False`. Requested directory paths may not contain symlinks.


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
errors, including when opening the configured root. Listing the configured root itself is also supported.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

On POSIX, a scanned descendant is checked again by identity before results
are returned. A detected move or replacement causes the scan to fail.

Service-owned defaults cap scans at 100,000 entries, results at 10,000, returned
JSON at 1 MiB, and elapsed scanning at two seconds. These constructor fields
(`max_scanned_entries`, `max_results`, `max_return_bytes`,
`max_elapsed_seconds`) are not agent-call parameters. Limit exhaustion returns
an explicit error and an empty result rather than successful partial data.
Time checks are cooperative and cannot interrupt a filesystem call blocked in
the kernel. Success responses obey `max_return_bytes`. Error responses truncate
echoed input and diagnostics to at most 4 KiB, or the configured byte budget
when smaller, with a 256-byte minimum to preserve a structured error envelope.

Symlinks are listed as entries with `is_dir=False`, including links to
directories. Classification never dereferences the target. Full paths name the
listed entries, rather than their targets. Sorting uses the original name to
break case-insensitive ties deterministically.

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
