# swarmauri_evaluator_subprocess

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_evaluator_subprocess</strong></p>
<p align="center">A subprocess-based evaluator for executing and measuring program performance in isolated subprocesses</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_subprocess/"><img alt="pypi: swarmauri_evaluator_subprocess" src="https://img.shields.io/pypi/v/swarmauri_evaluator_subprocess?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_subprocess/"><img alt="Monthly PyPI downloads: swarmauri_evaluator_subprocess" src="https://img.shields.io/pypi/dm/swarmauri_evaluator_subprocess?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/README.md"><img alt="README hits: swarmauri_evaluator_subprocess" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_evaluator_subprocess/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`SubprocessEvaluator` executes programs inside sandboxed subprocesses while
enforcing CPU, memory, and file size quotas. It captures stdout/stderr, tracks
exit codes, and returns a normalized score plus structured metadata describing
each run.

### Why This Package

`swarmauri_evaluator_subprocess` isolates this responsibility: A subprocess-based evaluator for executing and measuring program performance in isolated subprocesses. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py) exposes `SubprocessEvaluator`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_evaluator_subprocess` when your integration needs a subprocess-based evaluator for executing and measuring program performance in isolated subprocesses. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Apply CPU timeouts, memory ceilings, file size limits, and process count caps
  before user code starts (`resource.setrlimit`).
- Automatically choose the appropriate command: launch executables directly or
  wrap Python and shell scripts with the correct interpreter.
- Compare stdout against an `expected_output` string and annotate mismatches in
  the result metadata.
- Record execution context (`command`, `args`, `working_dir`) alongside
  collected streams for easy debugging.
- Aggregate multiple runs with reason counts, timeout rates, and success rates
  via `aggregate_scores`.

### Non-Goals

`swarmauri_evaluator_subprocess` owns a subprocess-based evaluator for executing and measuring program performance in isolated subprocesses. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Pick the tool that matches your workflow:

```bash
# pip
pip install swarmauri_evaluator_subprocess

# Poetry
poetry add swarmauri_evaluator_subprocess

# uv
uv add swarmauri_evaluator_subprocess
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_evaluator_subprocess
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_evaluator_subprocess
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_evaluator_subprocess
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

The example below writes a temporary Python script to disk, wraps it in a small
`IProgram` implementation, and evaluates it inside a subprocess. The evaluator
returns `1.0` when the exit code is in `success_exit_codes` and, when provided,
stdout matches `expected_output`.


**Evaluation options**

`SubprocessEvaluator.evaluate(program, **kwargs)` accepts runtime controls in
addition to the evaluator's model fields:

| Argument         | Description |
| ---------------- | ----------- |
| `args`           | List of command-line arguments appended to the prepared command. |
| `input_data`     | String provided on stdin; useful for feeding sample input. |
| `expected_output`| Optional stdout string; mismatches lower the score to `0.7`. |
| `timeout`        | Overrides the evaluator's `timeout` for a single run. |

**Returned metadata**

Each evaluation returns `(score, metadata)` where `metadata` always contains:

- `stdout`, `stderr`, and `exit_code` from the subprocess.
- `timed_out` flag plus a human-readable `reason` such as `success`,
  `timeout`, or `exit_code_<value>`.
- `command`, `args`, and `working_dir` to show how the program was launched.
- `execution_time` (seconds) measured by the evaluator wrapper.

When aggregating multiple runs, `aggregate_scores` adds `reason_counts`,
`timeout_rate`, `success_rate`, and `total_executions` to the combined
metadata so callers can evaluate fleet-wide behavior.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/docs/readme/quick_start.py).

```python
from pathlib import Path
import tempfile

from swarmauri_evaluator_subprocess import SubprocessEvaluator
from swarmauri_core.programs.IProgram import DiffType, IProgram


class ScriptProgram(IProgram):
    """Minimal IProgram wrapper for a script stored on disk."""

    def __init__(self, path: Path):
        self._path = Path(path)

    # Required IProgram interface methods -------------------------------
    def diff(self, other: IProgram) -> DiffType:  # pragma: no cover - example
        return {}

    def apply_diff(
        self, diff: DiffType
    ) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    def validate(self) -> bool:  # pragma: no cover
        return self._path.exists()

    def clone(self) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    # Methods consumed by SubprocessEvaluator ---------------------------
    def get_path(self) -> str:
        return str(self._path)

    def is_executable(self) -> bool:
        return False


def run_example(expected_output: str = "hello from subprocess\n"):
    evaluator = SubprocessEvaluator(timeout=5)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "echo.py"
        script_path.write_text(
            "print('hello from subprocess')\n", encoding="utf-8"
        )

        program = ScriptProgram(script_path)

        score, metadata = evaluator.evaluate(
            program,
            expected_output=expected_output,
        )

    return score, metadata


def main():
    score, metadata = run_example()
    print("Score:", score)
    print("Stdout:", metadata["stdout"].strip())
    print("Reason:", metadata["reason"])


if __name__ == "__main__":
    main()
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_evaluator_subprocess` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/docs/readme/usage.py).

```python
from pathlib import Path
import tempfile

from swarmauri_evaluator_subprocess import SubprocessEvaluator
from swarmauri_core.programs.IProgram import DiffType, IProgram


class ScriptProgram(IProgram):
    """Minimal IProgram wrapper for a script stored on disk."""

    def __init__(self, path: Path):
        self._path = Path(path)

    # Required IProgram interface methods -------------------------------
    def diff(self, other: IProgram) -> DiffType:  # pragma: no cover - example
        return {}

    def apply_diff(
        self, diff: DiffType
    ) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    def validate(self) -> bool:  # pragma: no cover
        return self._path.exists()

    def clone(self) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    # Methods consumed by SubprocessEvaluator ---------------------------
    def get_path(self) -> str:
        return str(self._path)

    def is_executable(self) -> bool:
        return False


def run_example(expected_output: str = "hello from subprocess\n"):
    evaluator = SubprocessEvaluator(timeout=5)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "echo.py"
        script_path.write_text(
            "print('hello from subprocess')\n", encoding="utf-8"
        )

        program = ScriptProgram(script_path)

        score, metadata = evaluator.evaluate(
            program,
            expected_output=expected_output,
        )

    return score, metadata


def main():
    score, metadata = run_example()
    print("Score:", score)
    print("Stdout:", metadata["stdout"].strip())
    print("Reason:", metadata["reason"])


if __name__ == "__main__":
    main()
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_evaluator_subprocess` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_evaluator_subprocess` source raises `FileNotFoundError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_evaluator_subprocess` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SubprocessEvaluator`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_evaluator_subprocess` is located in `standards` and owns a subprocess-based evaluator for executing and measuring program performance in isolated subprocesses. Source-declared APIs include `SubprocessEvaluator`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_evaluator_subprocess`.

Source-declared exports or types: `SubprocessEvaluator`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.evaluators` → `SubprocessEvaluator` → `swarmauri_evaluator_subprocess:SubprocessEvaluator`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_evaluator_subprocess` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_evaluator_subprocess` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_evaluator_subprocess`, use the source-declared public interfaces (`SubprocessEvaluator`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_evaluator_subprocess` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_evaluator_subprocess`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py). The `swarmauri_evaluator_subprocess` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_evaluator_subprocess` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_evaluator_subprocess` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/tests/example/test_readme_example.py)
- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_SubprocessEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/tests/unit/test_SubprocessEvaluator.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_evaluator_subprocess` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_evaluator_subprocess` provides a subprocess-based evaluator for executing and measuring program performance in isolated subprocesses; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_evaluator_subprocess`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_evaluator_subprocess` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/swarmauri_evaluator_subprocess/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml) provide the supporting context for `swarmauri_evaluator_subprocess`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_evaluator_subprocess](https://pypi.org/project/swarmauri_evaluator_subprocess/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_evaluator_subprocess` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_evaluator_subprocess` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_evaluator_subprocess` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_evaluator_subprocess` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_evaluator_subprocess` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_subprocess/NOTICE) for attribution.
<!-- readme-standards:end notices -->
