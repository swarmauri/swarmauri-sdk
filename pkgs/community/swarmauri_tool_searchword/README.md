![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_searchword/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_searchword/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_searchword/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_searchword.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_searchword" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_searchword?label=swarmauri_tool_searchword&color=green" alt="PyPI - swarmauri_tool_searchword"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Search Word

`swarmauri_tool_searchword` is a Swarmauri file-analysis tool for finding
case-insensitive word or phrase matches inside UTF-8 text files. It returns the
total match count and a line-by-line view with matching lines highlighted, which
makes it useful for documentation QA, terminology enforcement, audit workflows,
and agent-assisted text review.

## Why Use Swarmauri Tool Search Word

- Count repeated terms or phrases inside local text files.
- Surface matching lines for agent answers, reviews, and diagnostics.
- Enforce style-guide or terminology rules in docs and content pipelines.
- Reuse a simple search primitive inside larger Swarmauri toolchains.

## FAQ

> **What inputs does the tool expect?**  
> It expects a string `file_path` and a string `search_word`.

> **Is the search case-sensitive?**  
> No. Matching is case-insensitive.

> **What does the tool return?**  
> A dictionary with `count` and `lines`, where `lines` contains every line from
> the file and highlights matching lines with ANSI color codes.

> **Does it only search single words?**  
> No. It can search multi-word phrases as well.

## Features

- Case-insensitive search across UTF-8 text files.
- Returns both total occurrence count and full-file line output.
- Highlights matching lines using ANSI escape codes.
- Simple Swarmauri `ToolBase` interface for scripting and agents.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_searchword
```

```bash
pip install swarmauri_tool_searchword
```

## Usage

```python
from swarmauri_tool_searchword import SearchWordTool

tool = SearchWordTool()
result = tool(file_path="docs/README.md", search_word="swarmauri")

print(result["count"])
```

## Examples

### Scan documentation for banned terminology

```python
from pathlib import Path
from swarmauri_tool_searchword import SearchWordTool

tool = SearchWordTool()

for path in Path("docs").rglob("*.md"):
    result = tool(str(path), "utilize")
    if result["count"]:
        print(path, result["count"])
```

### Highlight policy terms in a compliance file

```python
from swarmauri_tool_searchword import SearchWordTool

tool = SearchWordTool()
result = tool("policies/security.txt", "retention period")

for line in result["lines"]:
    print(line)
```

### Use the tool in a Swarmauri workflow

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_searchword import SearchWordTool

tools = ToolCollection(tools=[SearchWordTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)
- [swarmauri_tool_dalechallreadability](https://pypi.org/project/swarmauri_tool_dalechallreadability/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Python `re` module documentation](https://docs.python.org/3/library/re.html)

## Best Practices

- Strip ANSI sequences before rendering in interfaces that do not support them.
- Use absolute or well-scoped relative paths in CI jobs.
- Reserve this tool for text files encoded as UTF-8.
- Combine match counts with readability tools when reviewing large content sets.

## License

This project is licensed under the Apache-2.0 License.
