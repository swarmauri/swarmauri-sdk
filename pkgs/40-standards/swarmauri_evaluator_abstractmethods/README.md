# swarmauri_evaluator_abstractmethods

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_evaluator_abstractmethods</strong></p>
<p align="center">An evaluator that verifies all methods in abstract base classes are properly marked as abstract</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_abstractmethods/"><img alt="pypi: swarmauri_evaluator_abstractmethods" src="https://img.shields.io/pypi/v/swarmauri_evaluator_abstractmethods"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_abstractmethods/"><img alt="Monthly PyPI downloads: swarmauri_evaluator_abstractmethods" src="https://img.shields.io/pypi/dm/swarmauri_evaluator_abstractmethods"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/README.md"><img alt="README hits: swarmauri_evaluator_abstractmethods" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_evaluator_abstractmethods/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`AbstractMethodsEvaluator` inspects Python source files to verify that abstract
base classes decorate their contract methods with `@abstractmethod`. The
evaluator is designed for automated program analysis within the Swarmauri
ecosystem and reports the exact lines that need attention together with summary
metrics.

### Why This Package

`swarmauri_evaluator_abstractmethods` isolates this responsibility: An evaluator that verifies all methods in abstract base classes are properly marked as abstract. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py) exposes `AbstractMethodsEvaluator`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_evaluator_abstractmethods` when your integration needs an evaluator that verifies all methods in abstract base classes are properly marked as abstract. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Parses Python modules into an AST to discover classes inheriting from
  `ABC` or any custom bases supplied through `abc_base_classes`.
- Flags methods on abstract classes that are missing the
  `@abstractmethod` decorator and records fully compliant methods for context.
- Ignores private (`_method`) and dunder (`__method__`) members by default to
  focus on the public interface; these rules can be toggled with
  `ignore_private` and `ignore_dunder`.
- Returns a detailed metadata payload containing compliance counts,
  per-method diagnostics, and an overall percentage score.
- Provides `aggregate_scores` to average multiple evaluation runs while
  combining their metadata such as total issues and compliance percentages.

### Non-Goals

`swarmauri_evaluator_abstractmethods` owns an evaluator that verifies all methods in abstract base classes are properly marked as abstract. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Install the evaluator with your preferred packaging tool:

```bash
pip install swarmauri_evaluator_abstractmethods
```

```bash
poetry add swarmauri_evaluator_abstractmethods
```

```bash
uv pip install swarmauri_evaluator_abstractmethods
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_evaluator_abstractmethods
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_evaluator_abstractmethods
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_evaluator_abstractmethods
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/docs/readme/quick_start.py).

```python
import textwrap
from typing import Dict

from swarmauri_core.programs.IProgram import DiffType, IProgram
from swarmauri_evaluator_abstractmethods import AbstractMethodsEvaluator


class InMemoryProgram(IProgram):
    def __init__(self, files: Dict[str, str]):
        self._files = files

    def diff(self, other: IProgram) -> DiffType:
        return {}

    def apply_diff(self, diff: DiffType) -> IProgram:
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> IProgram:
        return InMemoryProgram(dict(self._files))

    def get_source_files(self) -> Dict[str, str]:
        return self._files


def main() -> None:
    program = InMemoryProgram(
        {
            "shapes.py": textwrap.dedent(
                """
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self):
                        ...
                """
            ).strip(),
            "incomplete.py": textwrap.dedent(
                """
                from abc import ABC

                class InvalidShape(ABC):
                    def area(self):
                        ...
                """
            ).strip(),
        }
    )

    evaluator = AbstractMethodsEvaluator()
    score, metadata = evaluator.evaluate(program)

    print(f"Score: {score:.2f}")
    for issue in metadata["issues"]:
        if not issue["has_abstractmethod"]:
            print(f"{issue['file']}:{issue['line']} -> {issue['message']}")


if __name__ == "__main__":
    main()
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_evaluator_abstractmethods`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/docs/readme/usage.py).

```python
import textwrap
from typing import Dict

from swarmauri_core.programs.IProgram import DiffType, IProgram
from swarmauri_evaluator_abstractmethods import AbstractMethodsEvaluator


class InMemoryProgram(IProgram):
    def __init__(self, files: Dict[str, str]):
        self._files = files

    def diff(self, other: IProgram) -> DiffType:
        return {}

    def apply_diff(self, diff: DiffType) -> IProgram:
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> IProgram:
        return InMemoryProgram(dict(self._files))

    def get_source_files(self) -> Dict[str, str]:
        return self._files


def main() -> None:
    program = InMemoryProgram(
        {
            "shapes.py": textwrap.dedent(
                """
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self):
                        ...
                """
            ).strip(),
            "incomplete.py": textwrap.dedent(
                """
                from abc import ABC

                class InvalidShape(ABC):
                    def area(self):
                        ...
                """
            ).strip(),
        }
    )

    evaluator = AbstractMethodsEvaluator()
    score, metadata = evaluator.evaluate(program)

    print(f"Score: {score:.2f}")
    for issue in metadata["issues"]:
        if not issue["has_abstractmethod"]:
            print(f"{issue['file']}:{issue['line']} -> {issue['message']}")


if __name__ == "__main__":
    main()
```
<!-- readme-standards:end example.usage -->

### Configuration

Instantiate the evaluator with optional keyword arguments:

| Option | Default | Description |
| --- | --- | --- |
| `ignore_private` | `True` | Skip methods whose names begin with a single underscore. |
| `ignore_dunder` | `True` | Skip dunder methods such as `__init__`. |
| `abc_base_classes` | `["ABC", "abc.ABC"]` | Additional base class names that should be treated as abstract. |

### Error Handling

The inspected `swarmauri_evaluator_abstractmethods` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py).

### Best Practices

Use the explicit `swarmauri_evaluator_abstractmethods` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AbstractMethodsEvaluator`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_evaluator_abstractmethods` is located in `standards` and owns an evaluator that verifies all methods in abstract base classes are properly marked as abstract. Source-declared APIs include `AbstractMethodsEvaluator`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_evaluator_abstractmethods`.

Source-declared exports or types: `AbstractMethodsEvaluator`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.evaluators` → `AbstractMethodsEvaluator` → `swarmauri_evaluator_abstractmethods:AbstractMethodsEvaluator`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_evaluator_abstractmethods` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_evaluator_abstractmethods` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_evaluator_abstractmethods`, use the source-declared public interfaces (`AbstractMethodsEvaluator`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_evaluator_abstractmethods` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_evaluator_abstractmethods`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py). The `swarmauri_evaluator_abstractmethods` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_evaluator_abstractmethods` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_evaluator_abstractmethods` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/tests/test_readme_example.py)
- [tests/unit/test_AbstractMethodsEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/tests/unit/test_AbstractMethodsEvaluator.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_evaluator_abstractmethods` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_evaluator_abstractmethods` provides an evaluator that verifies all methods in abstract base classes are properly marked as abstract; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_evaluator_abstractmethods`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_evaluator_abstractmethods` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/swarmauri_evaluator_abstractmethods/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml) provide the supporting context for `swarmauri_evaluator_abstractmethods`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_evaluator_abstractmethods](https://pypi.org/project/swarmauri_evaluator_abstractmethods/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_evaluator_abstractmethods` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Evaluation Output**

Calling `evaluate` returns `(score, metadata)` where `score` is the ratio of
properly decorated methods to the total number of methods that should be
abstract. `metadata` contains:

- `issues`: A list of dictionaries with file, line, class name, method name,
  whether the decorator is present, and a descriptive message. Fully compliant
  methods are included for context.
- `total_abstract_classes`, `total_methods`, `total_abstract_methods`, and
  `total_missing_decorators`: Counters summarizing the analysis.
- `percentage_compliant`: Convenience metric equal to `score * 100`.

**Usage Example**

```python
import textwrap
from typing import Dict

from swarmauri_core.programs.IProgram import DiffType, IProgram
from swarmauri_evaluator_abstractmethods import AbstractMethodsEvaluator


class InMemoryProgram(IProgram):
    def __init__(self, files: Dict[str, str]):
        self._files = files

    def diff(self, other: IProgram) -> DiffType:
        return {}

    def apply_diff(self, diff: DiffType) -> IProgram:
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> IProgram:
        return InMemoryProgram(dict(self._files))

    def get_source_files(self) -> Dict[str, str]:
        return self._files


def main() -> None:
    program = InMemoryProgram(
        {
            "shapes.py": textwrap.dedent(
                """
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self):
                        ...
                """
            ).strip(),
            "incomplete.py": textwrap.dedent(
                """
                from abc import ABC

                class InvalidShape(ABC):
                    def area(self):
                        ...
                """
            ).strip(),
        }
    )

    evaluator = AbstractMethodsEvaluator()
    score, metadata = evaluator.evaluate(program)

    print(f"Score: {score:.2f}")
    for issue in metadata["issues"]:
        if not issue["has_abstractmethod"]:
            print(f"{issue['file']}:{issue['line']} -> {issue['message']}")


if __name__ == "__main__":
    main()
```

**Output**

```
Score: 0.50
incomplete.py:4 -> Method 'area' in abstract class 'InvalidShape' should be decorated with @abstractmethod
```

The evaluator reports both compliant and non-compliant methods in
`metadata["issues"]`, allowing you to surface violations while still retaining
context about classes that already satisfy the contract.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_evaluator_abstractmethods` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_evaluator_abstractmethods` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_evaluator_abstractmethods` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_abstractmethods/NOTICE) for attribution.
<!-- readme-standards:end notices -->
