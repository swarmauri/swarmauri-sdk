![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_createfile/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_createfile/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_createfile/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_createfile.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_createfile/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="PyPI - Python Version"/></a>
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
Path("/tmp/reports").mkdir(parents=True, exist_ok=True)

tool = CreateFileTool()

result = tool(
    path="/tmp/reports/summary.txt",
    content="Quarterly summary\n",
)
# {"created": True, "path": "/tmp/reports/summary.txt", "bytes_written": 18}

# Nothing is written when the path is already taken.
result = tool(path="/tmp/reports/summary.txt", content="overwrite attempt")
# {"created": False, "path": "/tmp/reports/summary.txt",
#  "error": "Something already exists at /tmp/reports/summary.txt. Nothing was written."}
```

### Result keys

| Key | Type | Meaning |
| --- | --- | --- |
| `created` | `bool` | Whether a file was written |
| `path` | `str` | Resolved destination path |
| `bytes_written` | `int` | Size of the written file, present only on success |
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
> No. A missing parent directory is reported in `error` rather than created, so
> a typo cannot silently produce a tree of directories.

> **Does it overwrite?**  
> Never. There is no overwrite flag by design; delete the file first if that is
> what you mean.

> **Is binary content supported?**  
> No. The tool writes text as UTF-8 only.
