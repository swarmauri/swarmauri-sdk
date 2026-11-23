# swarmauri_evaluator_anyusage

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_evaluator_anyusage</strong></p>
<p align="center">An evaluator component that detects and penalizes usage of the `Any` type in Python code</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_anyusage/"><img alt="pypi: swarmauri_evaluator_anyusage" src="https://img.shields.io/pypi/v/swarmauri_evaluator_anyusage"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_anyusage/"><img alt="Monthly PyPI downloads: swarmauri_evaluator_anyusage" src="https://img.shields.io/pypi/dm/swarmauri_evaluator_anyusage"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/README.md"><img alt="README hits: swarmauri_evaluator_anyusage" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_evaluator_anyusage/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Evaluator that detects and penalizes usage of the `typing.Any` type in Python source files.

### Why This Package

`swarmauri_evaluator_anyusage` isolates this responsibility: An evaluator component that detects and penalizes usage of the `Any` type in Python code. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py) exposes `AnyTypeUsageEvaluator`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_evaluator_anyusage` when your integration needs an evaluator component that detects and penalizes usage of the `Any` type in Python code. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Recursively scans every `.py` file under `program.path`, falling back to the current
  working directory when that attribute is missing.
- Uses the Python AST to capture imports and annotations plus a regex pass to
  backfill edge cases (e.g., syntax errors).
- Deducts `penalty_per_occurrence` (default `0.1`) for each finding and caps the
  deduction at `max_penalty` (default `1.0`), yielding a normalized score between `0.0`
  and `1.0` where higher is better.
- Returns rich metadata that lists the number of files analyzed, the total `Any`
  occurrences, and per-file line numbers and snippets to accelerate remediation.

### Non-Goals

`swarmauri_evaluator_anyusage` owns an evaluator component that detects and penalizes usage of the `Any` type in Python code. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that best fits your workflow:

```bash
# pip
pip install swarmauri_evaluator_anyusage

# Poetry
poetry add swarmauri_evaluator_anyusage

# uv
uv add swarmauri_evaluator_anyusage
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_evaluator_anyusage
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_evaluator_anyusage
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_evaluator_anyusage
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_base.programs.ProgramBase import ProgramBase
from swarmauri_evaluator_anyusage import AnyTypeUsageEvaluator


workspace = Path("path/to/project")

program = ProgramBase()
program.name = workspace.name
program.path = str(
    workspace
)  # AnyTypeUsageEvaluator walks this directory on disk

evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.1, max_penalty=1.0)
score, metadata = evaluator.evaluate(program)

print(f"Score: {score:.2f}")
print("Files analyzed:", metadata["files_analyzed"])
print("Any usages:", metadata["total_any_occurrences"])

for report in metadata["detailed_occurrences"]:
    print("-", report["file"])
    for occurrence in report["occurrences"]:
        print(f"  line {occurrence['line']}: {occurrence['context']}")

# If you already depend on `swarmauri_standard`, import
# `from swarmauri_standard.programs.Program import Program` and replace the
# ProgramBase construction above with `Program.from_workspace(workspace)`
# before setting `program.path` to keep the on-disk directory in sync with
# your Program content.
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_evaluator_anyusage` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_base.programs.ProgramBase import ProgramBase
from swarmauri_evaluator_anyusage import AnyTypeUsageEvaluator


workspace = Path("path/to/project")

program = ProgramBase()
program.name = workspace.name
program.path = str(
    workspace
)  # AnyTypeUsageEvaluator walks this directory on disk

evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.1, max_penalty=1.0)
score, metadata = evaluator.evaluate(program)

print(f"Score: {score:.2f}")
print("Files analyzed:", metadata["files_analyzed"])
print("Any usages:", metadata["total_any_occurrences"])

for report in metadata["detailed_occurrences"]:
    print("-", report["file"])
    for occurrence in report["occurrences"]:
        print(f"  line {occurrence['line']}: {occurrence['context']}")

# If you already depend on `swarmauri_standard`, import
# `from swarmauri_standard.programs.Program import Program` and replace the
# ProgramBase construction above with `Program.from_workspace(workspace)`
# before setting `program.path` to keep the on-disk directory in sync with
# your Program content.
```
<!-- readme-standards:end example.usage -->

**Metadata reference**

The evaluation metadata contains:

- `files_analyzed`: Number of Python files inspected.
- `total_any_occurrences`: Count of detected `Any` usages across all files.
- `penalty_applied`: The aggregate deduction applied to the score.
- `detailed_occurrences`: A list with one entry per file containing the absolute path
  and the line/context pairs for each finding. Multiple entries can share a line number
  when both the parameter and return annotations use `Any`; the `context` value explains
  the exact usage (import, parameter annotation, return annotation, etc.).
- `execution_time`: Added by `EvaluatorBase` to show how long the evaluation took.

Use these fields to build dashboards, enforce quality gates, or guide manual reviews.

### Configuration

Configure `swarmauri_evaluator_anyusage` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_evaluator_anyusage` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py).

### Best Practices

Use the explicit `swarmauri_evaluator_anyusage` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AnyTypeUsageEvaluator`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_evaluator_anyusage` is located in `standards` and owns an evaluator component that detects and penalizes usage of the `Any` type in Python code. Source-declared APIs include `AnyTypeUsageEvaluator`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_evaluator_anyusage`.

Source-declared exports or types: `AnyTypeUsageEvaluator`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.evaluators` → `AnyTypeUsageEvaluator` → `swarmauri_evaluator_anyusage:AnyTypeUsageEvaluator`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_evaluator_anyusage` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_evaluator_anyusage` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_evaluator_anyusage`, use the source-declared public interfaces (`AnyTypeUsageEvaluator`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_evaluator_anyusage` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_evaluator_anyusage`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py). The `swarmauri_evaluator_anyusage` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_evaluator_anyusage` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_evaluator_anyusage` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/tests/example/test_readme_example.py)
- [tests/unit/test_AnyTypeUsageEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/tests/unit/test_AnyTypeUsageEvaluator.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_evaluator_anyusage` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_evaluator_anyusage` provides an evaluator component that detects and penalizes usage of the `Any` type in Python code; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_evaluator_anyusage`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_evaluator_anyusage` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/swarmauri_evaluator_anyusage/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml) provide the supporting context for `swarmauri_evaluator_anyusage`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_evaluator_anyusage](https://pypi.org/project/swarmauri_evaluator_anyusage/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_evaluator_anyusage` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_evaluator_anyusage` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_evaluator_anyusage` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_evaluator_anyusage` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_evaluator_anyusage` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_anyusage/NOTICE) for attribution.
<!-- readme-standards:end notices -->
