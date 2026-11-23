# swarmauri_evaluator_constanttime

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_evaluator_constanttime</strong></p>
<p align="center">Evaluator that detects timing side channels using fixed-vs-random test</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_constanttime/"><img alt="pypi: swarmauri_evaluator_constanttime" src="https://img.shields.io/pypi/v/swarmauri_evaluator_constanttime"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluator_constanttime/"><img alt="Monthly PyPI downloads: swarmauri_evaluator_constanttime" src="https://img.shields.io/pypi/dm/swarmauri_evaluator_constanttime"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/README.md"><img alt="README hits: swarmauri_evaluator_constanttime" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_evaluator_constanttime/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Evaluator that detects timing side channels using a fixed-vs-random strategy.
It times a callable with repeated fixed inputs and compares those timings against
randomly generated inputs. Welch's t-test and Cliff's delta are used to decide
whether the observed runtime differences are statistically significant. The
evaluator reports a score of `1.0` for constant-time behaviour and `0.0`
otherwise, together with rich metadata about the underlying measurements.

### Why This Package

`swarmauri_evaluator_constanttime` isolates this responsibility: Evaluator that detects timing side channels using fixed-vs-random test. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py) exposes `ConstantTimeEvaluator`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_evaluator_constanttime` when your integration needs evaluator that detects timing side channels using fixed-vs-random test. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `TvlaResult`: declared in swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py
- `CliffResult`: declared in swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py
- `ConstantTimeEvaluator`: Check whether a function exhibits constant-time behavior.

### Non-Goals

`swarmauri_evaluator_constanttime` owns evaluator that detects timing side channels using fixed-vs-random test. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_evaluator_constanttime
```
<!-- readme-standards:end installation.uv -->

```bash
uv venv
source .venv/bin/activate
uv pip install swarmauri_evaluator_constanttime
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_evaluator_constanttime
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_evaluator_constanttime
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_evaluator_constanttime
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_evaluator_constanttime
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/docs/readme/quick_start.py).

```python
import secrets
import time

from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_constanttime import ConstantTimeEvaluator


class DummyProgram(IProgram):
    def diff(self, other: "IProgram"):
        return ()

    def apply_diff(self, diff):
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> "IProgram":
        return DummyProgram()


def insecure_compare(secret: bytes, guess: bytes) -> bool:
    for secret_byte, guess_byte in zip(secret, guess):
        if secret_byte != guess_byte:
            return False
        time.sleep(0.0001)
    return len(secret) == len(guess)


def make_input_pair() -> tuple[bytes, bytes]:
    return secrets.token_bytes(16), secrets.token_bytes(16)


def main() -> None:
    evaluator = ConstantTimeEvaluator()
    score, metadata = evaluator._compute_score(
        program=DummyProgram(),
        fn=insecure_compare,
        make_input_pair=make_input_pair,
        fixed_pair=(b"A" * 16, b"A" * 16),
        n_samples=20,
        iters_per=5,
    )

    print(f"Score: {score:.1f}")
    print(f"Constant time? {metadata['constant_time']}")
    print(f"t-statistic: {metadata['t_stat']:.2f}")
    print(f"Cliff's delta: {metadata['cliff_delta']:.3f}")

    assert metadata["constant_time"] is False


if __name__ == "__main__":
    main()
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_evaluator_constanttime` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/docs/readme/usage.py).

```python
import secrets
import time

from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_constanttime import ConstantTimeEvaluator


class DummyProgram(IProgram):
    def diff(self, other: "IProgram"):
        return ()

    def apply_diff(self, diff):
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> "IProgram":
        return DummyProgram()


def insecure_compare(secret: bytes, guess: bytes) -> bool:
    for secret_byte, guess_byte in zip(secret, guess):
        if secret_byte != guess_byte:
            return False
        time.sleep(0.0001)
    return len(secret) == len(guess)


def make_input_pair() -> tuple[bytes, bytes]:
    return secrets.token_bytes(16), secrets.token_bytes(16)


def main() -> None:
    evaluator = ConstantTimeEvaluator()
    score, metadata = evaluator._compute_score(
        program=DummyProgram(),
        fn=insecure_compare,
        make_input_pair=make_input_pair,
        fixed_pair=(b"A" * 16, b"A" * 16),
        n_samples=20,
        iters_per=5,
    )

    print(f"Score: {score:.1f}")
    print(f"Constant time? {metadata['constant_time']}")
    print(f"t-statistic: {metadata['t_stat']:.2f}")
    print(f"Cliff's delta: {metadata['cliff_delta']:.3f}")

    assert metadata["constant_time"] is False


if __name__ == "__main__":
    main()
```
<!-- readme-standards:end example.usage -->

The example below evaluates a deliberately leaky string comparison that sleeps
for every matching byte. Fixed inputs run all the way through the comparison and
take measurably longer than random guesses that fail fast, so the evaluator
flags the function as *not* constant time.

### Configuration

Configure `swarmauri_evaluator_constanttime` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_evaluator_constanttime` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py).

### Best Practices

Use the explicit `swarmauri_evaluator_constanttime` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ConstantTimeEvaluator`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_evaluator_constanttime` is located in `standards` and owns evaluator that detects timing side channels using fixed-vs-random test. Source-declared APIs include `ConstantTimeEvaluator`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_evaluator_constanttime`.

Source-declared exports or types: `ConstantTimeEvaluator`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.evaluators` → `ConstantTimeEvaluator` → `swarmauri_evaluator_constanttime:ConstantTimeEvaluator`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_evaluator_constanttime` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_evaluator_constanttime` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_evaluator_constanttime`, use the source-declared public interfaces (`ConstantTimeEvaluator`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_evaluator_constanttime` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_evaluator_constanttime`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py). The `swarmauri_evaluator_constanttime` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_evaluator_constanttime` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_evaluator_constanttime` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/tests/test_readme_example.py)
- [tests/unit/test_ConstantTimeEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/tests/unit/test_ConstantTimeEvaluator.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_evaluator_constanttime` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_evaluator_constanttime` provides evaluator that detects timing side channels using fixed-vs-random test; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_evaluator_constanttime`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_evaluator_constanttime` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/swarmauri_evaluator_constanttime/ConstantTimeEvaluator.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml) provide the supporting context for `swarmauri_evaluator_constanttime`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_evaluator_constanttime](https://pypi.org/project/swarmauri_evaluator_constanttime/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_evaluator_constanttime` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_evaluator_constanttime` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_evaluator_constanttime` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_evaluator_constanttime` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_evaluator_constanttime` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_evaluator_constanttime/NOTICE) for attribution.
<!-- readme-standards:end notices -->
