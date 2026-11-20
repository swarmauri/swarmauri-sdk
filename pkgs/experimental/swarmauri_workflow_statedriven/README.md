# swarmauri_workflow_statedriven

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_workflow_statedriven</strong></p>
<p align="center">Swarmauri&#x27;s StateDrivenWorkflow</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_workflow_statedriven/"><img alt="pypi: swarmauri_workflow_statedriven" src="https://img.shields.io/pypi/v/swarmauri_workflow_statedriven"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_workflow_statedriven/"><img alt="Monthly PyPI downloads: swarmauri_workflow_statedriven" src="https://img.shields.io/pypi/dm/swarmauri_workflow_statedriven"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/README.md"><img alt="README hits: swarmauri_workflow_statedriven" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/experimental/swarmauri_workflow_statedriven/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_workflow_statedriven`: Swarmauri's StateDrivenWorkflow

### Why This Package

`swarmauri_workflow_statedriven` isolates this responsibility: Swarmauri's StateDrivenWorkflow. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py) exposes `StateDrivenExecutionDriver`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_workflow_statedriven` when your integration needs swarmauri's StateDrivenWorkflow. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `WorkflowBase`: File: workflows/base.py
- `Condition`: Base class for all transition and join conditions.
- `AndCondition`: File: swarmauri/workflows/conditions/composite_condition.py
- `OrCondition`: File: swarmauri/workflows/conditions/composite_condition.py
- `NotCondition`: File: swarmauri/workflows/conditions/composite_condition.py
- `FunctionCondition`: Wraps a simple Python callable as a workflow condition.
- `MembershipCondition`: File: membership_condition.py
- `RegexCondition`: File: regex_condition.py

### Non-Goals

`swarmauri_workflow_statedriven` owns swarmauri's StateDrivenWorkflow. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `pyppeteer`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_workflow_statedriven
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_workflow_statedriven
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_workflow_statedriven
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_workflow_statedriven
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/docs/readme/quick_start.py).

```python
from swarmauri_workflow_statedriven.graph import WorkflowGraph

workflow = WorkflowGraph()
# Define nodes and transitions...
result = workflow.execute(start="start", initial_input={})
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_workflow_statedriven` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/docs/readme/usage.py).

```python
from swarmauri_workflow_statedriven.graph import WorkflowGraph

workflow = WorkflowGraph()
# Define nodes and transitions...
result = workflow.execute(start="start", initial_input={})
```
<!-- readme-standards:end example.usage -->

For more details, see the `docs` directory.

### Configuration

Configure `swarmauri_workflow_statedriven` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_workflow_statedriven` source raises `InvalidTransitionError`, `ValueError`, `WorkflowError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_workflow_statedriven` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `StateDrivenExecutionDriver`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_workflow_statedriven` is located in `experimental` and owns swarmauri's StateDrivenWorkflow. Source-declared APIs include `StateDrivenExecutionDriver`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_workflow_statedriven`.

Source-declared exports or types: `StateDrivenExecutionDriver`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.execution_drivers` → `StateDrivenExecutionDriver` → `swarmauri_workflow_statedriven:StateDrivenExecutionDriver`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_workflow_statedriven` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `pyppeteer`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_workflow_delegatedresearch`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_workflow_statedriven`, use the source-declared public interfaces (`StateDrivenExecutionDriver`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_workflow_statedriven` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_workflow_statedriven`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py). The `swarmauri_workflow_statedriven` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_workflow_statedriven` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_workflow_statedriven` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/tests/i9n/test_usage.py)
- [tests/unit/test_base.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/tests/unit/test_base.py)
- [tests/unit/test_exceptions.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/tests/unit/test_exceptions.py)
- [tests/unit/test_execution_driver.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/tests/unit/test_execution_driver.py)
- [tests/unit/test_graph.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/tests/unit/test_graph.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_workflow_statedriven` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_workflow_statedriven` provides swarmauri's StateDrivenWorkflow; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_workflow_statedriven`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_workflow_statedriven` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/swarmauri_workflow_statedriven/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml) provide the supporting context for `swarmauri_workflow_statedriven`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_workflow_statedriven](https://pypi.org/project/swarmauri_workflow_statedriven/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_workflow_statedriven`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/experimental/swarmauri_workflow_statedriven` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Execution controller integration**

`StateDrivenExecutionDriver(graph=graph, definition_version="1")` reuses
existing conditions, input modes, joins and merge strategies while returning
one durable node boundary per step. An optional authorized dispatcher routes
nodes through the shared invoker. Queues, results, join buffers and JSON
strategy state survive reconstruction; custom strategies can override their
checkpoint codec. Change the definition version when the graph changes.
Existing graph execution methods and transition constructors remain supported.
See the [composition guide](../../../docs/examples/composable-execution/README.md).

An experimental state-driven workflow engine for building graph-based processes using nodes and transitions. It supports conditions, join strategies, merge strategies and input modes to control execution flow.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_workflow_statedriven` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_workflow_statedriven` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_workflow_statedriven` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_workflow_statedriven/NOTICE) for attribution.
<!-- readme-standards:end notices -->
