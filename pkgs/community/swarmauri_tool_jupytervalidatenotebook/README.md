![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytervalidatenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytervalidatenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupytervalidatenotebook?label=swarmauri_tool_jupytervalidatenotebook&color=green" alt="PyPI - swarmauri_tool_jupytervalidatenotebook"/></a>
</p>

---

# Swarmauri Tool · Jupyter Validate Notebook

A Swarmauri tool that validates Jupyter notebooks (`NotebookNode` objects) against the official nbformat JSON schema. Use it to gate notebook submissions, enforce structural best practices, or wire schema checks into automated notebook pipelines.

- Accepts in-memory `NotebookNode` instances and produces structured success/error payloads.
- Surfaces detailed schema violations coming from nbformat/jsonschema.
- Integrates with Swarmauri agents via the standard tool registration workflow.

## Requirements

- Python 3.10 – 3.13.
- `nbformat` (installed automatically) with access to the notebook JSON schema.
- Dependencies (`jsonschema`, `swarmauri_base`, `swarmauri_standard`, `pydantic`, `typing_extensions`).

## Installation

Pick the installer that matches your workflow; each command resolves transitive packages.

**pip**

```bash
pip install swarmauri_tool_jupytervalidatenotebook
```

**Poetry**

```bash
poetry add swarmauri_tool_jupytervalidatenotebook
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_jupytervalidatenotebook

# or install into the active environment without touching pyproject.toml
uv pip install swarmauri_tool_jupytervalidatenotebook
```

> Tip: When using uv inside this repo, run uv commands from the repository root so it can locate the shared `pyproject.toml`.

## Quick Start

Load a notebook with nbformat, then pass the resulting `NotebookNode` to the tool. The response dictionary contains string values for `valid` (`"True"` or `"False"`) and a human-readable `report`.

```python
import nbformat
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

notebook = nbformat.read("analysis.ipynb", as_version=4)
validate = JupyterValidateNotebookTool()

result = validate(notebook)

if result["valid"] == "True":
    print("Notebook passes schema validation")
else:
    raise ValueError(result["report"])
```

## Usage Scenarios

### Batch Validate an Entire Notebook Directory

```python
import nbformat
from pathlib import Path
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

validator = JupyterValidateNotebookTool()
notebook_dir = Path("notebooks")

for path in notebook_dir.glob("**/*.ipynb"):
    nb = nbformat.read(path, as_version=4)
    result = validator(nb)
    status = "PASS" if result["valid"] == "True" else "FAIL"
    print(f"[{status}] {path}: {result['report']}")
```

Drop this snippet into CI to stop merges when any notebook violates the schema.

### Fail a Build When Validation Fails

```python
import sys
import nbformat
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

validator = JupyterValidateNotebookTool()
notebook = nbformat.read(sys.argv[1], as_version=4)
result = validator(notebook)

print(result["report"])
if result["valid"] != "True":
    sys.exit(1)
```

Wire the script into a pre-commit hook or build step (`python validate.py path/to/notebook.ipynb`).

### Combine With Other Swarmauri Tools

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

start_kernel = JupyterStartKernelTool()
validate_notebook = JupyterValidateNotebookTool()

launch = start_kernel()
print(f"Launched kernel: {launch['kernel_id']}")

# After generating a notebook programmatically, load and validate it
import nbformat
nb = nbformat.read("generated.ipynb", as_version=4)
validation = validate_notebook(nb)
print(validation)
```

Use the validation step after automated notebook generation/execution to ensure outputs remain schema-compliant.

## Troubleshooting

- **`Invalid nbformat version`** – The tool enforces nbformat version 4. Upgrade the notebook (`nbformat.convert`) or save it with a modern Jupyter client.
- **`Validation error`** – Inspect the `report` field for the jsonschema path causing the failure. Missing metadata or malformed cells are common culprits.
- **`Unexpected error`** – Log the exception and confirm the input is an nbformat `NotebookNode`, not a raw dict or path string.

## License

`swarmauri_tool_jupytervalidatenotebook` is released under the Apache 2.0 License. See `LICENSE` for full text.
