![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_createfile/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_createfile" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_createfile/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_createfile.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_createfile/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_createfile" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_createfile/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_createfile" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_createfile/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_createfile?label=swarmauri_tool_createfile&color=green" alt="PyPI - swarmauri_tool_createfile"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Create File

`swarmauri_tool_createfile` is a Swarmauri tool for creating a new text file at
a given path, optionally with initial content. It is meant for agent workflows
that need to write a generated report, a scaffolded module, a note, or any other
plain-text artifact to disk without shelling out.

## Features

- **Create a file with content** in a single call, written as UTF-8.
- **Create an empty file** when no content is supplied.
- **Never overwrites.** If anything already exists at the path, the call
  reports it and writes nothing.
- **Reports problems instead of raising.** A missing parent directory, an
  existing file, or an OS-level write failure all come back as a structured
  result, so an agent can read the reason and pick another path.
- **Expands `~`** so home-relative paths work without extra handling.
- **Restricts writes to trusted roots** configured by the service owner.
  Symlinks and parent traversal are rejected.

## Installation

```bash
# With uv
uv add swarmauri_tool_createfile

# With pip
pip install swarmauri_tool_createfile
```

## Usage

```python
from pathlib import Path

from swarmauri_tool_createfile import CreateFileTool

# The tool does not create parent directories, so make the parent first.
reports = Path.cwd() / "reports"
reports.mkdir(parents=True, exist_ok=True)

tool = CreateFileTool(allowed_roots=[str(reports)])

result = tool(
    path=str(reports / "summary.txt"),
    content="Quarterly summary\n",
)
# {"created": True, "path": ".../reports/summary.txt", "bytes_written": 18}

# Nothing is written when the path is already taken.
result = tool(path=str(reports / "summary.txt"), content="overwrite attempt")
assert result["created"] is False
```

### Result keys

| Key | Type | Meaning |
| --- | --- | --- |
| `created` | `bool` | Whether creation and writing completed successfully |
| `path` | `str` | Absolute expanded destination on valid-path calls; original input on expansion failure |
| `bytes_written` | `int` | Size obtained from the open file descriptor, present only on success |
| `error` | `str` | Human-readable reason, present only on refusal |

## Expected workflows

- **Write generated output.** An agent produces text and persists it to a path
  chosen by the caller.
- **Scaffold before editing.** Create the file, then let a separate editing tool
  modify it.
- **Fail safely.** Callers check `created` rather than wrapping the call in
  `try`, because refusals are values, not exceptions.

## FAQ

> **Does it create parent directories?**  
> Create the parent directory first. On POSIX, configure the existing parent
> as an allowed root when the service controls that directory and its ancestors.

> **Does it overwrite?**  
> Never. There is no overwrite flag by design; delete the file first if that is
> what you mean.

> **Is binary content supported?**  
> No. The tool writes text as UTF-8 only.

## Filesystem policy and failure behavior

The service owner configures `allowed_roots` as existing absolute directories.
The default is the working directory at tool construction. This configuration
is not an agent-call parameter. Relative destinations are interpreted against
the working directory at call time and must still lie beneath an allowed root.
An empty root list denies all writes. Existing symlinks anywhere in the root or
destination path are rejected; `..` components are rejected rather than resolved.

On POSIX, the destination must be a direct child of a configured root.
Configure the destination's existing parent as an allowed root only when
the service controls that directory and its ancestors. This avoids
creating through a nested parent that can move outside the root during
lookup. Creation uses one exclusive, no-follow lookup from the root
descriptor. Linux uses `openat2` to open the configured root when
available. If the syscall is unavailable, the tool walks the trusted root
path without following symlinks. Policy denials such as `EPERM` or
`EACCES` are returned as errors.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

UTF-8 encoding is checked before creation. Exclusive creation atomically refuses
existing entries, including dangling symlinks; writing the full content is not an
atomic publication. If an OS write, descriptor-stat, or close operation fails,
`created` is false and the error warns that partial output may remain. The tool
does not unlink the final pathname, because another process may have replaced
it. Service-owned recovery must inspect incomplete output rather than blindly
deleting or retrying at the same pathname.

### Windows filesystem support

On Windows the backend opens the local drive by its volume identity and
opens each component relative to a held directory handle. It rejects junctions
and other reparse points and does not accept UNC or device paths, alternate data
streams, or ambiguous trailing dots or spaces, or reserved DOS basenames. Ancestors are
opened for traversal without requiring listing access. Volume and directory handles
deny delete sharing during traversal. Returned paths are descriptive snapshots.
Existing entries, including hard links, cannot be overwritten by exclusive
creation.
