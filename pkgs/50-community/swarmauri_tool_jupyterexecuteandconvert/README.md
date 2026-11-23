# swarmauri_tool_jupyterexecuteandconvert

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_jupyterexecuteandconvert</strong></p>
<p align="center">Swarmauri notebook publishing tool for executing Jupyter notebooks and converting them to rendered output formats.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/"><img alt="pypi: swarmauri_tool_jupyterexecuteandconvert" src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecuteandconvert?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/"><img alt="Monthly PyPI downloads: swarmauri_tool_jupyterexecuteandconvert" src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecuteandconvert?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/README.md"><img alt="README hits: swarmauri_tool_jupyterexecuteandconvert" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_jupyterexecuteandconvert` runs a notebook through the `jupyter nbconvert` CLI, writes an executed notebook artifact, and then converts that executed notebook to a target output format such as HTML or PDF.

### Why This Package

`swarmauri_tool_jupyterexecuteandconvert` isolates this responsibility: Swarmauri notebook publishing tool for executing Jupyter notebooks and converting them to rendered output formats. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py) exposes `JupyterExecuteAndConvertTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_jupyterexecuteandconvert` when your integration needs swarmauri notebook publishing tool for executing Jupyter notebooks and converting them to rendered output formats. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Verifies the source notebook exists before execution.
- Executes notebooks with `jupyter nbconvert --execute`.
- Converts the executed notebook in a second `nbconvert` step.
- Supports `html` and `pdf` output formats.
- Returns either `{"converted_file": ..., "status": "success"}` or an error payload.

### Non-Goals

`swarmauri_tool_jupyterexecuteandconvert` owns swarmauri notebook publishing tool for executing Jupyter notebooks and converting them to rendered output formats. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml) declares runtime dependencies including `nbconvert`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_jupyterexecuteandconvert
```

```bash
pip install swarmauri_tool_jupyterexecuteandconvert
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_jupyterexecuteandconvert
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_jupyterexecuteandconvert
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_jupyterexecuteandconvert
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/docs/readme/quick_start.py).

```python
from swarmauri_tool_jupyterexecuteandconvert import (
    JupyterExecuteAndConvertTool,
)

tool = JupyterExecuteAndConvertTool()
result = tool(
    notebook_path="reports/weekly.ipynb",
    output_format="html",
    execution_timeout=300,
)

print(result)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_jupyterexecuteandconvert` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/docs/readme/usage.py).

```python
from swarmauri_tool_jupyterexecuteandconvert import (
    JupyterExecuteAndConvertTool,
)

tool = JupyterExecuteAndConvertTool()
result = tool(
    notebook_path="reports/weekly.ipynb",
    output_format="html",
    execution_timeout=300,
)

print(result)
```
<!-- readme-standards:end example.usage -->

**Execute a notebook and export HTML**

```python
response = JupyterExecuteAndConvertTool()(
    notebook_path="reports/status.ipynb",
    output_format="html",
    execution_timeout=120,
)

print(response["converted_file"])
```

**Execute a notebook and export PDF**

```python
response = JupyterExecuteAndConvertTool()(
    notebook_path="reports/board_packet.ipynb",
    output_format="pdf",
    execution_timeout=600,
)

if "error" in response:
    print(response["message"])
```

### Configuration

Configure `swarmauri_tool_jupyterexecuteandconvert` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_jupyterexecuteandconvert` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py).

### Best Practices

Use the explicit `swarmauri_tool_jupyterexecuteandconvert` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JupyterExecuteAndConvertTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_jupyterexecuteandconvert` is located in `community` and owns swarmauri notebook publishing tool for executing Jupyter notebooks and converting them to rendered output formats. Source-declared APIs include `JupyterExecuteAndConvertTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_jupyterexecuteandconvert`.

Source-declared exports or types: `JupyterExecuteAndConvertTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `JupyterExecuteAndConvertTool` → `swarmauri_tool_jupyterexecuteandconvert:JupyterExecuteAndConvertTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_jupyterexecuteandconvert` are `nbconvert`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_toolkit_jupytertoolkit`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_tool_jupyterexecuteandconvert`, use the source-declared public interfaces (`JupyterExecuteAndConvertTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_jupyterexecuteandconvert` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_jupyterexecuteandconvert`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py). The `swarmauri_tool_jupyterexecuteandconvert` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_jupyterexecuteandconvert` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_jupyterexecuteandconvert` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_JupyterExecuteAndConvertTool.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/tests/unit/test_JupyterExecuteAndConvertTool.py)
- [tests/unit/test_JupyterExecuteAndConvertTool__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/tests/unit/test_JupyterExecuteAndConvertTool__init__.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_jupyterexecuteandconvert` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

- Execute notebooks and publish rendered artifacts in one Swarmauri tool call.
- Keep notebook reporting workflows inside a simple automation surface.
- Produce web or document outputs from the exact executed notebook state.

**What file does this tool convert?**

It first creates an executed notebook named `executed_<original>.ipynb`, then converts that executed notebook to the requested format.

**Does this return notebook content?**

No. It returns metadata about the produced converted file, not the notebook object itself.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_jupyterexecuteandconvert`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/swarmauri_tool_jupyterexecuteandconvert/JupyterExecuteAndConvertTool.py) for the exact types and signatures involved.

### When

**When should I use this instead of swarmauri_tool_jupyterexecutenotebook?**

Use this package when you want rendered artifacts like HTML or PDF. Use `swarmauri_tool_jupyterexecutenotebook` when you want the executed `NotebookNode` in memory.

---

## Documentation and Related Packages

### More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbconvert documentation](https://nbconvert.readthedocs.io/)
- [Jupyter documentation](https://jupyter.org/documentation)

### Related Packages

- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)
- [`swarmauri_tool_jupyterexecutenotebookwithparameters`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/)
- [`swarmauri_tool_jupyterexporthtml`](https://pypi.org/project/swarmauri_tool_jupyterexporthtml/)
- [`swarmauri_tool_jupyterexportlatex`](https://pypi.org/project/swarmauri_tool_jupyterexportlatex/)
- [`swarmauri_tool_jupyterexportpython`](https://pypi.org/project/swarmauri_tool_jupyterexportpython/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_jupyterexecuteandconvert](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_jupyterexecuteandconvert`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_jupyterexecuteandconvert` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_jupyterexecuteandconvert` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_jupyterexecuteandconvert` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupyterexecuteandconvert/NOTICE) for attribution.
<!-- readme-standards:end notices -->
