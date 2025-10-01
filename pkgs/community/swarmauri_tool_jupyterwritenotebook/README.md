![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterwritenotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterwritenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterwritenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterwritenotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterwritenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterwritenotebook?label=swarmauri_tool_jupyterwritenotebook&color=green" alt="PyPI - swarmauri_tool_jupyterwritenotebook"/></a>
</p>

---

# Swarmauri Tool · Jupyter Write Notebook

A Swarmauri automation tool that serializes Jupyter `NotebookNode` objects (or compatible dictionaries) to disk using the nbformat JSON schema. It encapsulates validation, encoding, and integrity checks so pipelines can persist generated notebooks with confidence.

- Writes notebooks with pretty-printed JSON (`indent=2`) and `ensure_ascii=False` for readable diffs and Unicode safety.
- Performs a read-back verification step to guarantee the file contains valid JSON data.
- Slots directly into agent workflows via the standard Swarmauri tool registration system.

## Requirements

- Python 3.10 – 3.13.
- `nbformat` for working with notebook structures.
- Dependencies (`swarmauri_base`, `swarmauri_standard`, `pydantic`). These install automatically with the package.

## Installation

Choose the installer that matches your workflow—each command pulls transitive dependencies.

**pip**

```bash
pip install swarmauri_tool_jupyterwritenotebook
```

**Poetry**

```bash
poetry add swarmauri_tool_jupyterwritenotebook
```

**uv**

```bash
# Add to the active project and update uv.lock
uv add swarmauri_tool_jupyterwritenotebook

# or install into the current environment without modifying pyproject.toml
uv pip install swarmauri_tool_jupyterwritenotebook
```

> Tip: When using uv in this repository, run commands from the repo root so uv can resolve the shared `pyproject.toml`.

## Quick Start

Generate a notebook programmatically and persist it with the tool. The response dictionary includes either a success message and file path or an error string.

```python
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

nb = new_notebook(
    cells=[
        new_markdown_cell("# Metrics Report"),
        new_code_cell("print('accuracy:', 0.91)")
    ],
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    }
)

write_notebook = JupyterWriteNotebookTool()
result = write_notebook(notebook_data=nb, output_file="reports/metrics.ipynb")

print(result)
# {'message': 'Notebook written successfully', 'file_path': 'reports/metrics.ipynb'}
```

## Usage Scenarios

### Persist Notebook Output From an Agent

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

registry = ToolRegistry()
registry.register(JupyterWriteNotebookTool())
agent = Agent(tool_registry=registry)

# Agent actions produce notebook JSON (truncated for brevity)
notebook_payload = {
    "cells": [
        {"cell_type": "code", "source": "print('done')", "metadata": {}, "outputs": []}
    ],
    "metadata": {"kernelspec": {"name": "python3"}},
    "nbformat": 4,
    "nbformat_minor": 5
}

response = agent.tools["JupyterWriteNotebookTool"](
    notebook_data=notebook_payload,
    output_file="runs/output.ipynb"
)
print(response)
```

Register the tool alongside other Swarmauri components so agents can emit notebooks as part of a conversation or workflow.

### Convert Executed Notebooks to Artifacts

```python
import nbformat
from nbformat import NotebookNode
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

# Assume executed_notebook is a NotebookNode returned by nbconvert or papermill
executed_notebook: NotebookNode = nbformat.read("executed.ipynb", as_version=4)
executed_notebook.metadata.setdefault("tags", []).append("validated")

writer = JupyterWriteNotebookTool()
artifact = writer(notebook_data=executed_notebook, output_file="artifacts/executed.ipynb")
print(artifact)
```

This pattern is useful for CI systems that run notebooks and archive the executed results for review.

### Chain With Validation Before Publishing

```python
import nbformat
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

nb = nbformat.read("draft.ipynb", as_version=4)
validate = JupyterValidateNotebookTool()
write = JupyterWriteNotebookTool()

validation = validate(nb)
if validation["valid"] != "True":
    raise RuntimeError(validation["report"])

result = write(notebook_data=nb, output_file="dist/published.ipynb")
print(result)
```

Validate the notebook schema first, then persist the approved version for distribution.

## Troubleshooting

- **`An error occurred during notebook write operation`** – The tool surfaces file-system exceptions verbatim. Check write permissions and ensure the target directory exists.
- **Empty file after execution** – Read-back verification triggers when the file cannot be parsed as JSON. Confirm the notebook structure is JSON serializable (e.g., use nbformat helper constructors).
- **Unexpected characters** – The tool writes with `ensure_ascii=False` so non-ASCII text remains intact. If your environment cannot handle UTF-8, pass a different `encoding` argument.

## License

`swarmauri_tool_jupyterwritenotebook` is released under the Apache 2.0 License. See `LICENSE` for the full text.
