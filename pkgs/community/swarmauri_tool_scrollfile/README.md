<p align="center">
  <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg" alt="Swarmauri" width="420"/>
</p>

<p align="center">
  <a href="https://pepy.tech/project/swarmauri_tool_scrollfile/"><img src="https://static.pepy.tech/badge/swarmauri_tool_scrollfile/month" alt="Monthly downloads"/></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_scrollfile/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_scrollfile.svg" alt="Repository hits"/></a>
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_scrollfile" alt="Supported Python versions"/></a>
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/l/swarmauri_tool_scrollfile" alt="License"/></a>
  <a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img src="https://img.shields.io/pypi/v/swarmauri_tool_scrollfile?label=release" alt="Release version"/></a>
</p>

# Swarmauri Tool Scroll File

`swarmauri_tool_scrollfile` gives agents and workflows a bounded way to inspect
large UTF-8 text files. It returns numbered lines together with stable previous
and next page positions, avoiding full-file output.

## Features

- Reads at most the requested page size into the result.
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
from swarmauri_tool_scrollfile import ScrollFileTool

tool = ScrollFileTool()
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

## Workflow Integration

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_scrollfile import ScrollFileTool

tools = ToolCollection(tools=[ScrollFileTool()])
```

## Performance

The tool streams from the start of the file to the requested page and holds at
most one page plus one lookahead line in memory. Memory use is `O(page_size)`;
runtime is `O(start_line + page_size)` for a stateless request.

## License

This package is licensed under Apache-2.0.
