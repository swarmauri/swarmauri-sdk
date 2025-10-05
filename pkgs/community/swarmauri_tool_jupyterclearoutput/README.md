![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterclearoutput" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterclearoutput/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterclearoutput.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterclearoutput" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterclearoutput" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterclearoutput?label=swarmauri_tool_jupyterclearoutput&color=green" alt="PyPI - swarmauri_tool_jupyterclearoutput"/></a>
</p>

---

# Swarmauri Tool Jupyter Clear Output

Removes outputs and execution counts from Jupyter notebooks using a Swarmauri tool wrapper. Ideal for cleaning notebooks before publishing or committing to version control.

## Features

- Clears output arrays from all code cells and resets `execution_count` to `None`.
- Leaves markdown and raw cells untouched.
- Works with notebooks already loaded into memory (dict/JSON structure).

## Prerequisites

- Python 3.10 or newer.
- Dependencies: `nbconvert`, `swarmauri_base`, `swarmauri_standard` (installed automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterclearoutput

# poetry
poetry add swarmauri_tool_jupyterclearoutput

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterclearoutput
```

## Quickstart

```python
import json
from swarmauri_tool_jupyterclearoutput import JupyterClearOutputTool

notebook_data = json.loads(Path("notebooks/example.ipynb").read_text())

cleaner = JupyterClearOutputTool()
clean_notebook = cleaner(notebook_data)

Path("notebooks/example-clean.ipynb").write_text(json.dumps(clean_notebook, indent=2))
```

## Tips

- Run this tool before committing notebooks to keep diffs small and avoid leaking secrets in output cells.
- Combine with Swarmauri pipelines that regenerate notebooks (e.g., parameterized runs) to ensure clean artifacts.
- For large notebooks, consider streaming to disk rather than loading entirely into memory before clearing.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
