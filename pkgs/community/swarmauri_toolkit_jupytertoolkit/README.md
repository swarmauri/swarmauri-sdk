![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_toolkit_jupytertoolkit" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_jupytertoolkit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_jupytertoolkit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_toolkit_jupytertoolkit" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_jupytertoolkit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_jupytertoolkit?label=swarmauri_toolkit_jupytertoolkit&color=green" alt="PyPI - swarmauri_toolkit_jupytertoolkit"/></a>
</p>

---

# Swarmauri Toolkit · Jupyter Toolkit

A one-stop Swarmauri toolkit that bundles the Jupyter kernel, execution, export, and validation tools under a single interface. Instantiate `JupyterToolkit` and you instantly gain access to twenty standalone tools covering notebook lifecycle tasks: launching kernels, running cells, converting notebooks, exporting formats, and more.

- Pre-registers commonly used Jupyter utilities such as `JupyterStartKernelTool`, `JupyterExecuteNotebookTool`, `JupyterExportHtmlTool`, and `JupyterShutdownKernelTool`.
- Ensures each tool shares the same Swarmauri component metadata so agents can discover capabilities automatically.
- Useful for agents, pipelines, or CLI scripts that need rich notebook automation without manually wiring every tool.

## Requirements

- Python 3.10 – 3.13.
- The underlying Jupyter tool packages (installed automatically as dependencies).
- Access to a local or remote Jupyter runtime for kernel operations.

## Installation

Pick the package manager that fits your project; each command installs the toolkit plus all underlying Jupyter tools.

**pip**

```bash
pip install swarmauri_toolkit_jupytertoolkit
```

**Poetry**

```bash
poetry add swarmauri_toolkit_jupytertoolkit
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_toolkit_jupytertoolkit

# or install into the active environment without modifying pyproject.toml
uv pip install swarmauri_toolkit_jupytertoolkit
```

> Tip: Some tools depend on Jupyter client libraries (`jupyter_client`, `nbformat`, `nbconvert`). Make sure your environment includes any system packages required by those libraries (for example LaTeX when exporting to PDF/LaTeX).

## Quick Start

```python
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

toolkit = JupyterToolkit()

# Start a kernel and execute a notebook
start = toolkit.tools["JupyterStartKernelTool"]()
print(start)

run = toolkit.tools["JupyterExecuteNotebookTool"](
    notebook_path="reports/daily.ipynb",
    timeout=120
)
print(run)

# Export the executed notebook to HTML
export = toolkit.tools["JupyterExportHtmlTool"](
    notebook_path="reports/daily.ipynb",
    output_path="reports/daily.html"
)
print(export)

# Gracefully shut down the kernel
shutdown = toolkit.tools["JupyterShutdownKernelTool"](
    kernel_id=start["kernel_id"],
    shutdown_timeout=10
)
print(shutdown)
```

`JupyterToolkit.tools` is a dictionary keyed by tool name. Each entry is the ready-to-call Swarmauri tool instance.

## Usage Scenarios

### Build a Notebook Orchestration Service

```python
from fastapi import FastAPI, BackgroundTasks
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

app = FastAPI()
toolkit = JupyterToolkit()

@app.post("/execute")
def execute(data: dict, background: BackgroundTasks):
    nb_path = data["notebook_path"]
    background.add_task(
        toolkit.tools["JupyterExecuteNotebookWithParametersTool"],
        notebook_path=nb_path,
        parameters=data.get("parameters", {})
    )
    return {"status": "queued", "notebook": nb_path}
```

Trigger parameterized notebook runs via HTTP and reuse the toolkit’s pre-wired execution tool.

### Enhance a Swarmauri Agent With Notebook Skills

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

jupyter_toolkit = JupyterToolkit()
registry = ToolRegistry()
registry.register(jupyter_toolkit.tools["JupyterExecuteCellTool"])
registry.register(jupyter_toolkit.tools["JupyterReadNotebookTool"])
registry.register(jupyter_toolkit.tools["JupyterWriteNotebookTool"])

agent = Agent(tool_registry=registry)
response = agent.run(HumanMessage(content="Execute cell 3 from analytics.ipynb"))
print(response)
```

Combine multiple notebook operations so the agent can read, modify, and execute notebooks within a single conversation.

### Convert Notebooks in Bulk

```python
from pathlib import Path
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

toolkit = JupyterToolkit()
export_html = toolkit.tools["JupyterExportHtmlTool"]
export_md = toolkit.tools["JupyterExportMarkdownTool"]

for notebook in Path("notebooks").glob("*.ipynb"):
    export_html(notebook_path=str(notebook), output_path=str(notebook.with_suffix(".html")))
    export_md(notebook_path=str(notebook), output_path=str(notebook.with_suffix(".md")))
```

Run multiple exporters without manually instantiating each tool.

## Troubleshooting

- **Kernel start failures** – Ensure the environment has a working Jupyter kernelspec (e.g., `python3`). Check permissions when running inside containers or restricted hosts.
- **Export errors** – Some exporters (LaTeX/PDF) require external dependencies. Install TeX Live or pandoc as appropriate.
- **Tool lookup mistakes** – Use `toolkit.tools.keys()` to inspect available tool names; they map 1:1 to the underlying packages (`JupyterExecuteNotebookTool`, `JupyterValidateNotebookTool`, etc.).

## License

`swarmauri_toolkit_jupytertoolkit` is released under the Apache 2.0 License. See `LICENSE` for details.
