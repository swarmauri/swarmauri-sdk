# swarmauri_tool_jupytershutdownkernel

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_jupytershutdownkernel</strong></p>
<p align="center">Swarmauri notebook-lifecycle tool for shutting down Jupyter kernels programmatically with jupyter_client.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/"><img alt="pypi: swarmauri_tool_jupytershutdownkernel" src="https://img.shields.io/pypi/v/swarmauri_tool_jupytershutdownkernel"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/"><img alt="Monthly PyPI downloads: swarmauri_tool_jupytershutdownkernel" src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytershutdownkernel"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/README.md"><img alt="README hits: swarmauri_tool_jupytershutdownkernel" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_jupytershutdownkernel` is a Swarmauri notebook-lifecycle tool
for shutting down Jupyter kernels programmatically. It is useful for notebook
automation cleanup, CI teardown, resource reclamation, and agent workflows that
must terminate kernels after execution.

### Why This Package

- Stop Jupyter kernels cleanly after execution workflows complete.
- Reclaim compute and runtime resources in automated notebook pipelines.
- Provide a standard Swarmauri tool surface for kernel teardown.
- Return structured shutdown status suitable for orchestration and logging.

### When to Use

Choose `swarmauri_tool_jupytershutdownkernel` when your integration needs swarmauri notebook-lifecycle tool for shutting down Jupyter kernels programmatically with jupyter_client. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Swarmauri `ToolBase` implementation registered as `JupyterShutdownKernelTool`.
- Supports graceful shutdown with forced fallback.
- Reports structured success and error states.
- Useful for CI cleanup, notebook automation, and agent-managed kernels.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_tool_jupytershutdownkernel` owns swarmauri notebook-lifecycle tool for shutting down Jupyter kernels programmatically with jupyter_client. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml) declares runtime dependencies including `jupyter-client`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_jupytershutdownkernel
```

```bash
pip install swarmauri_tool_jupytershutdownkernel
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_jupytershutdownkernel
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_jupytershutdownkernel
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_jupytershutdownkernel
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/docs/readme/quick_start.py).

```python
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

tool = JupyterShutdownKernelTool()
result = tool(kernel_id="example-kernel-id", shutdown_timeout=5)

print(result)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_jupytershutdownkernel` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/docs/readme/usage.py).

```python
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

tool = JupyterShutdownKernelTool()
result = tool(kernel_id="example-kernel-id", shutdown_timeout=5)

print(result)
```
<!-- readme-standards:end example.usage -->

**Shut down a kernel by ID**

```python
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

tool = JupyterShutdownKernelTool()
result = tool("kernel-uuid-value", 5)

print(result["status"])
```

**Use after a start-kernel workflow**

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

starter = JupyterStartKernelTool()
shutdown = JupyterShutdownKernelTool()

launch = starter()
cleanup = shutdown(launch["kernel_id"])

print(cleanup)
```

**Register the tool in a Swarmauri collection**

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

tools = ToolCollection(tools=[JupyterShutdownKernelTool()])
print(tools)
```

### Configuration

Configure `swarmauri_tool_jupytershutdownkernel` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_jupytershutdownkernel` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py).

### Best Practices

- Keep track of the kernel ID returned by your startup workflow.
- Use explicit shutdown in CI and automation even when processes are short-lived.
- Increase the timeout for busy kernels that may need a little longer to exit.
- Run shutdown logic on the same host that owns the kernel runtime files.

---

## Package Boundary

### What It Owns

`swarmauri_tool_jupytershutdownkernel` is located in `community` and owns swarmauri notebook-lifecycle tool for shutting down Jupyter kernels programmatically with jupyter_client. Source-declared APIs include `JupyterShutdownKernelTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_jupytershutdownkernel`.

Source-declared exports or types: `JupyterShutdownKernelTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `JupyterShutdownKernelTool` → `swarmauri_tool_jupytershutdownkernel:JupyterShutdownKernelTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_jupytershutdownkernel` are `jupyter-client`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_toolkit_jupytertoolkit`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_tool_jupytershutdownkernel`, use the source-declared public interfaces (`JupyterShutdownKernelTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_jupytershutdownkernel` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_jupytershutdownkernel`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py). The `swarmauri_tool_jupytershutdownkernel` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_jupytershutdownkernel` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_jupytershutdownkernel` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_JupyterShutdownKernelTool.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/tests/unit/test_JupyterShutdownKernelTool.py)
- [tests/unit/test_JupyterShutdownKernelTool__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/tests/unit/test_JupyterShutdownKernelTool__init__.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_jupytershutdownkernel` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What inputs does the tool expect?**
> A `kernel_id` string and an optional `shutdown_timeout`.

> **What does the tool return?**
> A dictionary with `kernel_id`, `status`, and `message`.

> **How does it behave when graceful shutdown fails?**
> It attempts a forced shutdown if the kernel stays alive after the timeout.

> **What if the kernel cannot be found?**
> The tool returns an error status with a descriptive message.

### Why

**Why select this package?** `swarmauri_tool_jupytershutdownkernel` provides swarmauri notebook-lifecycle tool for shutting down Jupyter kernels programmatically with jupyter_client; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_jupytershutdownkernel`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/swarmauri_tool_jupytershutdownkernel/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_jupytershutdownkernel` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [jupyter_client documentation](https://jupyter-client.readthedocs.io/)
- [Jupyter kernels overview](https://docs.jupyter.org/en/latest/projects/kernels.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

### Related Packages

- [swarmauri_tool_jupyterstartkernel](https://pypi.org/project/swarmauri_tool_jupyterstartkernel/)
- [swarmauri_tool_jupyterexecutecell](https://pypi.org/project/swarmauri_tool_jupyterexecutecell/)
- [swarmauri_tool_jupyterruncell](https://pypi.org/project/swarmauri_tool_jupyterruncell/)
- [swarmauri_tool_jupyterclearoutput](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_jupytershutdownkernel](https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_jupytershutdownkernel`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_jupytershutdownkernel` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_jupytershutdownkernel` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_jupytershutdownkernel` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_jupytershutdownkernel` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_jupytershutdownkernel/NOTICE) for attribution.
<!-- readme-standards:end notices -->
