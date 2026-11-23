# swarmauri_toolkit_jupytertoolkit

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_toolkit_jupytertoolkit</strong></p>
<p align="center">A unified toolkit for aggregating standalone jupyter notebook tools.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/"><img alt="pypi: swarmauri_toolkit_jupytertoolkit" src="https://img.shields.io/pypi/v/swarmauri_toolkit_jupytertoolkit?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/"><img alt="Monthly PyPI downloads: swarmauri_toolkit_jupytertoolkit" src="https://img.shields.io/pypi/dm/swarmauri_toolkit_jupytertoolkit?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/README.md"><img alt="README hits: swarmauri_toolkit_jupytertoolkit" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A one-stop Swarmauri toolkit that bundles the Jupyter kernel, execution, export, and validation tools under a single interface. Instantiate `JupyterToolkit` and you instantly gain access to twenty standalone tools covering notebook lifecycle tasks: launching kernels, running cells, converting notebooks, exporting formats, and more.

- Pre-registers commonly used Jupyter utilities such as `JupyterStartKernelTool`, `JupyterExecuteNotebookTool`, `JupyterExportHtmlTool`, and `JupyterShutdownKernelTool`.
- Ensures each tool shares the same Swarmauri component metadata so agents can discover capabilities automatically.
- Useful for agents, pipelines, or CLI scripts that need rich notebook automation without manually wiring every tool.

### Why This Package

`swarmauri_toolkit_jupytertoolkit` isolates this responsibility: A unified toolkit for aggregating standalone jupyter notebook tools. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py) exposes `JupyterToolkit`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_toolkit_jupytertoolkit` when your integration needs a unified toolkit for aggregating standalone jupyter notebook tools. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `JupyterToolkit`: declared in swarmauri_toolkit_jupytertoolkit/JupyterToolkit.py

### Non-Goals

`swarmauri_toolkit_jupytertoolkit` owns a unified toolkit for aggregating standalone jupyter notebook tools. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Python 3.10 ? 3.13.
- The underlying Jupyter tool packages (installed automatically as dependencies).
- Access to a local or remote Jupyter runtime for kernel operations.

### Installation

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

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_toolkit_jupytertoolkit
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_toolkit_jupytertoolkit
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_toolkit_jupytertoolkit
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

`JupyterToolkit.tools` is a dictionary keyed by tool name. Each entry is the ready-to-call Swarmauri tool instance.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/docs/readme/quick_start.py).

```python
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

toolkit = JupyterToolkit()

# Start a kernel and execute a notebook
start = toolkit.tools["JupyterStartKernelTool"]()
print(start)

run = toolkit.tools["JupyterExecuteNotebookTool"](
    notebook_path="reports/daily.ipynb", timeout=120
)
print(run)

# Export the executed notebook to HTML
export = toolkit.tools["JupyterExportHtmlTool"](
    notebook_path="reports/daily.ipynb", output_path="reports/daily.html"
)
print(export)

# Gracefully shut down the kernel
shutdown = toolkit.tools["JupyterShutdownKernelTool"](
    kernel_id=start["kernel_id"], shutdown_timeout=10
)
print(shutdown)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_toolkit_jupytertoolkit` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/docs/readme/usage.py).

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
        parameters=data.get("parameters", {}),
    )
    return {"status": "queued", "notebook": nb_path}
```
<!-- readme-standards:end example.usage -->

**Build a Notebook Orchestration Service**


Trigger parameterized notebook runs via HTTP and reuse the toolkit?s pre-wired execution tool.

**Enhance a Swarmauri Agent With Notebook Skills**

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

**Convert Notebooks in Bulk**

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

### Configuration

Configure `swarmauri_toolkit_jupytertoolkit` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_toolkit_jupytertoolkit` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py).

### Best Practices

Use the explicit `swarmauri_toolkit_jupytertoolkit` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JupyterToolkit`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_toolkit_jupytertoolkit` is located in `community` and owns a unified toolkit for aggregating standalone jupyter notebook tools. Source-declared APIs include `JupyterToolkit`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_toolkit_jupytertoolkit`.

Source-declared exports or types: `JupyterToolkit`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.toolkits` → `JupyterToolkit` → `swarmauri_toolkit_jupytertoolkit:JupyterToolkit`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_toolkit_jupytertoolkit` are `pydantic`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-tool-jupyterclearoutput`, `swarmauri-tool-jupyterdisplay`, `swarmauri-tool-jupyterdisplayhtml`, `swarmauri-tool-jupyterexecuteandconvert`, `swarmauri-tool-jupyterexecutecell`, `swarmauri-tool-jupyterexecutenotebook`, `swarmauri-tool-jupyterexecutenotebookwithparameters`, `swarmauri-tool-jupyterexporthtml`, `swarmauri-tool-jupyterexportlatex`, `swarmauri-tool-jupyterexportmarkdown`, `swarmauri-tool-jupyterexportpython`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_toolkit_jupytertoolkit` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_toolkit_jupytertoolkit`, use the source-declared public interfaces (`JupyterToolkit`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_toolkit_jupytertoolkit` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_toolkit_jupytertoolkit`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py). The `swarmauri_toolkit_jupytertoolkit` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_toolkit_jupytertoolkit` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_toolkit_jupytertoolkit` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_JupyterToolkit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/tests/unit/test_JupyterToolkit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_toolkit_jupytertoolkit` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_toolkit_jupytertoolkit` provides a unified toolkit for aggregating standalone jupyter notebook tools; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_toolkit_jupytertoolkit`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_toolkit_jupytertoolkit` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/swarmauri_toolkit_jupytertoolkit/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml) provide the supporting context for `swarmauri_toolkit_jupytertoolkit`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_tool_jupyterclearoutput](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterclearoutput/README.md): Swarmauri notebook-cleanup tool for clearing code-cell outputs and execution counts from Jupyter notebooks.
- [swarmauri_tool_jupyterdisplay](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterdisplay/README.md): A tool designed to display rich media and object representations in a Jupyter Notebook using IPython's display functionality.
- [swarmauri_tool_jupyterdisplayhtml](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterdisplayhtml/README.md): A tool designed to render HTML content within a Jupyter Notebook using IPython's HTML display method.
- [swarmauri_tool_jupyterexecuteandconvert](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/README.md): Swarmauri notebook publishing tool for executing Jupyter notebooks and converting them to rendered output formats.
- [swarmauri_tool_jupyterexecutecell](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutecell/README.md): Swarmauri code-execution tool for running notebook cells in an active IPython environment with captured output.
- [swarmauri_tool_jupyterexecutenotebook](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/README.md): Swarmauri notebook-execution tool for running Jupyter notebooks with nbclient and capturing cell outputs.
- [swarmauri_tool_jupyterexecutenotebookwithparameters](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebookwithparameters/README.md): Swarmauri papermill tool for executing parameterized Jupyter notebooks and writing executed notebook outputs.
- [swarmauri_tool_jupyterexporthtml](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexporthtml/README.md): Swarmauri HTML publishing tool for rendering Jupyter notebooks with nbconvert and optional inline presentation assets.
- [swarmauri_tool_jupyterexportlatex](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexportlatex/README.md): Swarmauri publication-export tool for converting Jupyter notebooks into LaTeX and optional PDF artifacts.
- [swarmauri_tool_jupyterexportmarkdown](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexportmarkdown/README.md): Swarmauri Markdown publishing tool for converting Jupyter notebooks into documentation-ready Markdown.
- [swarmauri_tool_jupyterexportpython](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexportpython/README.md): Swarmauri code-extraction tool for converting Jupyter notebooks into Python scripts with nbconvert.
- [swarmauri_tool_jupyterfromdict](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterfromdict/README.md): Swarmauri notebook-construction tool for converting Python dictionaries into validated Jupyter NotebookNode objects.
- [swarmauri_tool_jupytergetiopubmessage](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytergetiopubmessage/README.md): A tool designed to retrieve messages from the IOPub channel of a Jupyter kernel using jupyter_client, capturing cell outputs and logs.
- [swarmauri_tool_jupytergetshellmessage](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytergetshellmessage/README.md): A tool designed to retrieve shell messages from a running Jupyter kernel using jupyter_client, useful for debugging execution responses.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_toolkit_jupytertoolkit](https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_toolkit_jupytertoolkit`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_toolkit_jupytertoolkit` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Troubleshooting**

- **Kernel start failures** ? Ensure the environment has a working Jupyter kernelspec (e.g., `python3`). Check permissions when running inside containers or restricted hosts.
- **Export errors** ? Some exporters (LaTeX/PDF) require external dependencies. Install TeX Live or pandoc as appropriate.
- **Tool lookup mistakes** ? Use `toolkit.tools.keys()` to inspect available tool names; they map 1:1 to the underlying packages (`JupyterExecuteNotebookTool`, `JupyterValidateNotebookTool`, etc.).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_toolkit_jupytertoolkit` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_toolkit_jupytertoolkit` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_toolkit_jupytertoolkit` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/LICENSE).
<!-- readme-standards:end license -->

`swarmauri_toolkit_jupytertoolkit` is released under the Apache 2.0 License. See `LICENSE` for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_jupytertoolkit/NOTICE) for attribution.
<!-- readme-standards:end notices -->
