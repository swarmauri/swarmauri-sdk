<p align="center">
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/dm/swarmauri_tool_scrollfile" alt="PyPI downloads"/></a>
  <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg" alt="Swarmauri" width="420"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/dm/swarmauri_tool_scrollfile" alt="Monthly downloads"/></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_scrollfile/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_scrollfile.svg" alt="Repository hits"/></a>
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_scrollfile" alt="Supported Python versions"/></a>
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/l/swarmauri_tool_scrollfile" alt="License"/></a>
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/v/swarmauri_tool_scrollfile?label=swarmauri_tool_scrollfile&color=green" alt="Release version"/></a>
</p>

# Swarmauri Tool Scroll File

`swarmauri_tool_scrollfile` gives agents and workflows a bounded way to inspect
large UTF-8 text files. It returns numbered lines together with stable previous
and next page positions, avoiding full-file output.

## Features

- Restricts reads to service-configured filesystem roots by default.
- Rejects symlinks unless the service owner explicitly opts in.
- Caps page size, scanned lines and bytes, individual-line size, elapsed
  time, and returned bytes.
- Navigates up or down using one-based line anchors.
- Returns line numbers and explicit previous/next page positions.
- Clamps an anchor beyond EOF to the final available page.
- Validates paths and navigation arguments before reading.
- Registers as a `swarmauri.tools` entry point.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_scrollfile
```

```bash
pip install swarmauri_tool_scrollfile
```

## Usage

```python
from pathlib import Path

from swarmauri_tool_scrollfile import ScrollFileTool

tool = ScrollFileTool(allowed_roots=[str(Path("logs").resolve())])
first_page = tool("logs/application.log")

if first_page["has_next"]:
    second_page = tool(
        "logs/application.log",
        start_line=first_page["next_start_line"],
        page_size=first_page["page_size"],
        direction="down",
    )
```

An upward request treats `start_line` as the current page anchor and returns
the preceding page:

```python
previous_page = tool(
    "logs/application.log",
    start_line=second_page["start_line"],
    page_size=second_page["page_size"],
    direction="up",
)
```

Each result contains `lines`, `start_line`, `end_line`, `page_size`,
`has_previous`, `has_next`, `previous_start_line`, and `next_start_line`.

## Security and Resource Limits

`file_path` is agent-controlled, but filesystem policy is not. The service
owner configures `allowed_roots` when creating the tool; requested paths are
canonically resolved and must remain inside one of those roots. Paths
containing symlinks are rejected by default, and the resolved target must be a
regular file.

```python
tool = ScrollFileTool(
    allowed_roots=["/srv/application-logs", "/srv/reports"],
)
```

The default root is the process working directory. Set `allow_symlinks=True`
only when following symlinks is part of the trusted service configuration.
`allow_unrestricted_paths=True` is a privileged opt-in that disables root
containment; use it only when the process already runs in a least-privilege
filesystem sandbox.

Each call enforces service-owned limits: at most 100 returned lines, 100,000
scanned lines, 8 MiB scanned data, 64 KiB per line, 256 KiB returned content,
and two seconds of file-reading time. Exceeding a limit raises `ValueError`
rather than returning a partial or ambiguous page.

## Workflow Integration

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_scrollfile import ScrollFileTool

tools = ToolCollection(
    tools=[ScrollFileTool(allowed_roots=["/srv/application-logs"])]
)
```

## Performance

The tool streams from the start of the file to the requested page and holds at
most one page plus one lookahead line in memory, subject to the limits above.
Memory use is `O(page_size)`; runtime is `O(start_line + page_size)` for a
stateless request.

## License

This package is licensed under Apache-2.0.


## Descriptor-based opening and page boundaries

Where Linux `openat2` is available, lookups use beneath-root resolution.
If the syscall is unavailable, the POSIX fallback opens a single child of
the trusted root with a no-follow lookup. Nested file lookups fail
with `ENOTSUP`. Policy denials such as `EPERM` or `EACCES` are returned as
errors, including when opening the configured root.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

`allow_symlinks=True` requires Linux `openat2` and permits only relative links
whose complete resolution stays beneath the selected root. Absolute links,
root escapes, and magic links are rejected. This intentionally narrows the old
opt-in. `allow_unrestricted_paths=True` anchors at the filesystem root; it does
not independently enable symlink following. Configured root paths cannot
contain symlinks or parent traversal.

Opened handles retain inode identity if directories are renamed. This prevents
symlink substitution from redirecting a read, but does not freeze file contents
or prevent another actor from moving an opened directory. Services must control
permissions on their trees.

The returned-content budget applies to the page actually returned, including
EOF fallback. The preceding rolling buffer is bounded separately by page size
and individual-line limits; large earlier lines no longer reject a small later
page merely because they exceed the return budget. A one-byte lookahead detects
the next page without decoding or line-validating its contents. That probe is
still charged against scanned-line and scanned-byte limits. Time checks remain
cooperative and cannot interrupt a filesystem syscall already blocked in the
kernel.

### Windows filesystem support

On Windows the backend opens the local drive by its volume identity and
opens each component relative to a held directory handle. It rejects junctions
and other reparse points and does not accept UNC or device paths, alternate data
streams, or ambiguous trailing dots or spaces, or reserved DOS basenames. Ancestors are
opened for traversal without requiring listing access. Volume and directory handles
deny delete sharing during traversal. Returned paths are descriptive snapshots.
Confined reads check the opened file and reject files with multiple
hard links. Filesystem permissions govern concurrent changes to file contents.
