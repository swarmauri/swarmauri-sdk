# swarmauri_tool_jupyterexecutenotebook

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_jupyterexecutenotebook</strong></p>
<p align="center">Swarmauri notebook-execution tool for running Jupyter notebooks with nbclient and capturing cell outputs.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/"><img alt="pypi: swarmauri_tool_jupyterexecutenotebook" src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutenotebook?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/"><img alt="Monthly PyPI downloads: swarmauri_tool_jupyterexecutenotebook" src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecutenotebook?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/README.md"><img alt="README hits: swarmauri_tool_jupyterexecutenotebook" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_jupyterexecutenotebook` executes every cell in a Jupyter notebook with `nbclient`, captures notebook outputs in-place, and returns the executed `NotebookNode` for downstream processing.

### Why This Package

`swarmauri_tool_jupyterexecutenotebook` isolates this responsibility: Swarmauri notebook-execution tool for running Jupyter notebooks with nbclient and capturing cell outputs. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py) exposes `JupyterExecuteNotebookTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_jupyterexecutenotebook` when your integration needs swarmauri notebook-execution tool for running Jupyter notebooks with nbclient and capturing cell outputs. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Loads notebooks from disk with `nbformat`.
- Executes all cells with `nbclient.NotebookClient`.
- Returns the executed notebook object rather than a file path.
- Supports per-cell execution timeout control.
- Uses `allow_errors=True`, so the notebook can retain partial outputs even when a cell fails.

### Non-Goals

`swarmauri_tool_jupyterexecutenotebook` owns swarmauri notebook-execution tool for running Jupyter notebooks with nbclient and capturing cell outputs. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml) declares runtime dependencies including `nbconvert`, `nbformat`, `ipykernel`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_jupyterexecutenotebook
```

```bash
pip install swarmauri_tool_jupyterexecutenotebook
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_jupyterexecutenotebook
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_jupyterexecutenotebook
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_jupyterexecutenotebook
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/docs/readme/quick_start.py).

```python
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

tool = JupyterExecuteNotebookTool()
executed = tool("notebooks/report.ipynb", timeout=60)

for cell in executed.cells:
    if cell.get("outputs"):
        print(cell["outputs"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_jupyterexecutenotebook` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/docs/readme/usage.py).

```python
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

tool = JupyterExecuteNotebookTool()
executed = tool("notebooks/report.ipynb", timeout=60)

for cell in executed.cells:
    if cell.get("outputs"):
        print(cell["outputs"])
```
<!-- readme-standards:end example.usage -->

**Execute a notebook before export**

```python
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

tool = JupyterExecuteNotebookTool()
notebook = tool("analytics/daily_metrics.ipynb", timeout=120)

print(len(notebook.cells))
```

**Inspect partial output after a failing cell**

```python
executed = JupyterExecuteNotebookTool()("debug/failing_notebook.ipynb")

for index, cell in enumerate(executed.cells):
    print(index, cell.get("outputs", []))
```

### Configuration

Configure `swarmauri_tool_jupyterexecutenotebook` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_jupyterexecutenotebook` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py).

### Best Practices

Use the explicit `swarmauri_tool_jupyterexecutenotebook` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JupyterExecuteNotebookTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_jupyterexecutenotebook` is located in `community` and owns swarmauri notebook-execution tool for running Jupyter notebooks with nbclient and capturing cell outputs. Source-declared APIs include `JupyterExecuteNotebookTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_jupyterexecutenotebook`.

Source-declared exports or types: `JupyterExecuteNotebookTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `JupyterExecuteNotebookTool` → `swarmauri_tool_jupyterexecutenotebook:JupyterExecuteNotebookTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_jupyterexecutenotebook` are `nbconvert`, `nbformat`, `ipykernel`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_toolkit_jupytertoolkit`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_tool_jupyterexecutenotebook`, use the source-declared public interfaces (`JupyterExecuteNotebookTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_jupyterexecutenotebook` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_jupyterexecutenotebook`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py). The `swarmauri_tool_jupyterexecutenotebook` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_jupyterexecutenotebook` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_jupyterexecutenotebook` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_JupyterExecuteNotebookTool.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/tests/unit/test_JupyterExecuteNotebookTool.py)
- [tests/unit/test_JupyterExecuteNotebookTool__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/tests/unit/test_JupyterExecuteNotebookTool__init__.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_jupyterexecutenotebook` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

- Run notebooks inside Swarmauri workflows without shelling out to a separate notebook runner.
- Capture generated outputs for reporting, validation, or export steps.
- Keep notebook execution inside a simple Python tool contract.

**What does this tool return?**

It returns the `NotebookNode` after execution. If execution fails partway through, the tool still returns the notebook object so callers can inspect partial output.

**Does it stop on the first cell error?**

No. The underlying client is created with `allow_errors=True`, which preserves notebook state and outputs even when cells fail.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_jupyterexecutenotebook`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/swarmauri_tool_jupyterexecutenotebook/JupyterExecuteNotebookTool.py) for the exact types and signatures involved.

### When

**When should I use this instead of the parameterized execution tool?**

Use this package for direct notebook execution. Use `swarmauri_tool_jupyterexecutenotebookwithparameters` when you need papermill-style parameter injection and an output notebook path.

---

## Documentation and Related Packages

### More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbclient documentation](https://nbclient.readthedocs.io/)
- [nbformat documentation](https://nbformat.readthedocs.io/)

### Related Packages

- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)
- [`swarmauri_tool_jupyterwritenotebook`](https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/)
- [`swarmauri_tool_jupyterexecutenotebookwithparameters`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/)
- [`swarmauri_tool_jupyterexecuteandconvert`](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
- [`swarmauri_tool_jupyterclearoutput`](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_jupyterexecutenotebook](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_jupyterexecutenotebook`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_jupyterexecutenotebook` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_jupyterexecutenotebook` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_jupyterexecutenotebook` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_jupyterexecutenotebook` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecutenotebook/NOTICE) for attribution.
<!-- readme-standards:end notices -->
