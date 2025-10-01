![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterdisplayhtml" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplayhtml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplayhtml.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterdisplayhtml" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterdisplayhtml" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterdisplayhtml?label=swarmauri_tool_jupyterdisplayhtml&color=green" alt="PyPI - swarmauri_tool_jupyterdisplayhtml"/></a>
</p>

---

# Swarmauri Tool Jupyter Display HTML

Specialized wrapper for displaying HTML snippets in Jupyter notebooks via IPython's `HTML` display helper.

## Features

- Accepts raw HTML strings and renders them inline in Jupyter.
- Returns status information (`success`/`error`) for integration with larger tool flows.
- Subclass of `ToolBase`, so it plugs into Swarmauri toolchains seamlessly.

## Prerequisites

- Python 3.10 or newer.
- Jupyter/IPython environment with display capabilities.

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterdisplayhtml

# poetry
poetry add swarmauri_tool_jupyterdisplayhtml

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterdisplayhtml
```

## Quickstart

```python
from swarmauri_tool_jupyterdisplayhtml import JupyterDisplayHTMLTool

tool = JupyterDisplayHTMLTool()
result = tool("""
<h2>Swarmauri</h2>
<p>This HTML was rendered by JupyterDisplayHTMLTool.</p>
""")
print(result)
```

## Tips

- Wrap the call in Swarmauri agents to surface generated HTML reports or tables.
- Validate user-provided HTML before rendering to avoid XSS issues in shared notebooks.
- Combine with other tools that produce HTML (e.g., Folium maps) to display results inline.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
