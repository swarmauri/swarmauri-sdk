![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_searchword" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_searchword/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_searchword.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_searchword" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_searchword" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_searchword?label=swarmauri_tool_searchword&color=green" alt="PyPI - swarmauri_tool_searchword"/></a>
</p>

---

# Swarmauri Tool · Search Word

A Swarmauri utility for counting case-insensitive word or phrase occurrences in text files. The tool highlights matching lines and returns both the count and the decorated text so you can surface findings in agent conversations or CI logs.

- Accepts any UTF-8 text file and performs case-insensitive matching.
- Preserves surrounding context by returning the full line with ANSI highlighting (red) when a match is found.
- Ships as a Swarmauri tool, so it can be registered alongside other agent capabilities.

## Requirements

- Python 3.10 – 3.13.
- No external libraries beyond the core Swarmauri dependencies (`swarmauri_base`, `swarmauri_standard`, `pydantic`).

## Installation

Choose the installer that matches your workflow; each command collects the required dependencies.

**pip**

```bash
pip install swarmauri_tool_searchword
```

**Poetry**

```bash
poetry add swarmauri_tool_searchword
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_searchword

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_searchword
```

> Tip: The tool reads files from disk, so ensure the executing process has permission to access the target path.

## Quick Start

```python
from swarmauri_tool_searchword import SearchWordTool

search = SearchWordTool()
result = search(file_path="docs/README.md", search_word="swarmauri")

print(result["count"])
# e.g., 5

for line in result["lines"]:
    print(line)
```

Matching lines are wrapped with ANSI escape codes (red foreground). When piping to logs or terminals that render ANSI, matches stand out immediately.

## Usage Scenarios

### Enforce Terminology in CI Pipelines

```python
from pathlib import Path
from swarmauri_tool_searchword import SearchWordTool

search = SearchWordTool()

for file in Path("docs").rglob("*.md"):
    result = search(file_path=str(file), search_word="utilize")
    if result["count"] > 0:
        raise SystemExit(f"Forbidden term found in {file}: {result['count']} occurrences")
```

Stop merges when banned words or phrases appear in documentation.

### Provide Explanations in an Agent Response

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_searchword import SearchWordTool

registry = ToolRegistry()
registry.register(SearchWordTool())
agent = Agent(tool_registry=registry)

message = HumanMessage(content="How many times do we mention 'latency' in docs/overview.txt?")
response = agent.run(message)
print(response)
```

Agents can report both the count and the highlighted context back to the user.

### Audit Configuration Files for Secrets

```python
from swarmauri_tool_searchword import SearchWordTool

search = SearchWordTool()
config_files = [".env", "config/production.ini"]

for path in config_files:
    result = search(file_path=path, search_word="api_key")
    if result["count"]:
        print(f"Potential secret reference in {path}: {result['count']} matches")
```

Quickly scan multiple configuration files when performing security reviews.

## Troubleshooting

- **`FileNotFoundError`** – Confirm the path is correct and accessible. Relative paths are resolved from the current working directory of the process invoking the tool.
- **`Invalid input`** – The tool only accepts string file paths and search terms. Validate arguments if they originate from user prompts.
- **ANSI escape codes in output** – If your consumer cannot render ANSI, strip the escape sequences before displaying (e.g., with `re.sub(r'\x1b\[[0-9;]*m', '', line)`).

## License

`swarmauri_tool_searchword` is released under the Apache 2.0 License. See `LICENSE` for full details.
