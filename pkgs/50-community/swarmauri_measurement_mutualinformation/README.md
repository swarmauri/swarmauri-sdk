# swarmauri_measurement_mutualinformation

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_measurement_mutualinformation</strong></p>
<p align="center">Mutual-information feature screening measurement for Swarmauri classification datasets using scikit-learn.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/"><img alt="pypi: swarmauri_measurement_mutualinformation" src="https://img.shields.io/pypi/v/swarmauri_measurement_mutualinformation?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_measurement_mutualinformation/"><img alt="Monthly PyPI downloads: swarmauri_measurement_mutualinformation" src="https://img.shields.io/pypi/dm/swarmauri_measurement_mutualinformation?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/README.md"><img alt="README hits: swarmauri_measurement_mutualinformation" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_measurement_mutualinformation/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_measurement_mutualinformation` is the Swarmauri feature-signal
measurement for supervised classification datasets. It wraps
`sklearn.feature_selection.mutual_info_classif` and returns the average mutual
information across all non-target columns in a Pandas DataFrame.

### Why This Package

- Estimate how strongly each feature depends on a discrete target before model
  training.
- Reduce low-signal columns earlier in a Swarmauri data or evaluation pipeline.
- Reuse a standard `MeasurementBase` component instead of hand-wiring feature
  scoring logic.
- Pair feature screening with downstream metrics, vectorization, or model
  selection flows.

### When to Use

Choose `swarmauri_measurement_mutualinformation` when your integration needs mutual-information feature screening measurement for Swarmauri classification datasets using scikit-learn. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Supervised mutual-information scoring for discrete targets.
- Automatic exclusion of the target column from the feature matrix.
- Returns one aggregate score that is easy to log, compare, or threshold.
- Uses the Swarmauri measurement interface for pipeline compatibility.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_measurement_mutualinformation` owns mutual-information feature screening measurement for Swarmauri classification datasets using scikit-learn. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml) declares runtime dependencies including `scikit-learn`, `pandas`, `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_measurement_mutualinformation
```

```bash
pip install swarmauri_measurement_mutualinformation
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_measurement_mutualinformation
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_measurement_mutualinformation
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_measurement_mutualinformation
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/docs/readme/quick_start.py).

```python
import pandas as pd
from swarmauri_measurement_mutualinformation import (
    MutualInformationMeasurement,
)

frame = pd.DataFrame(
    {
        "feature_a": [0, 1, 1, 0, 1, 0],
        "feature_b": [5.1, 5.0, 4.9, 5.2, 5.1, 5.0],
        "target": [0, 1, 1, 0, 1, 0],
    }
)

measurement = MutualInformationMeasurement()
score = measurement.calculate(frame, target_column="target")
print(score)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_measurement_mutualinformation` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/docs/readme/usage.py).

```python
import pandas as pd
from swarmauri_measurement_mutualinformation import (
    MutualInformationMeasurement,
)

frame = pd.DataFrame(
    {
        "feature_a": [0, 1, 1, 0, 1, 0],
        "feature_b": [5.1, 5.0, 4.9, 5.2, 5.1, 5.0],
        "target": [0, 1, 1, 0, 1, 0],
    }
)

measurement = MutualInformationMeasurement()
score = measurement.calculate(frame, target_column="target")
print(score)
```
<!-- readme-standards:end example.usage -->

**Screen a small classification dataset**

```python
import pandas as pd
from swarmauri_measurement_mutualinformation import MutualInformationMeasurement

data = pd.DataFrame(
    {
        "clicked_email": [1, 0, 1, 1, 0, 0],
        "days_active": [4, 2, 5, 6, 1, 2],
        "plan_tier": [2, 1, 2, 3, 1, 1],
        "converted": [1, 0, 1, 1, 0, 0],
    }
)

measurement = MutualInformationMeasurement()
print(measurement.calculate(data, target_column="converted"))
```

**Inspect per-feature scores directly**

```python
from sklearn.feature_selection import mutual_info_classif

X = frame.drop(columns=["target"])
y = frame["target"]

scores = mutual_info_classif(X, y)
for column, score in zip(X.columns, scores):
    print(column, score)
```

### Configuration

Configure `swarmauri_measurement_mutualinformation` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_measurement_mutualinformation` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py).

### Best Practices

- Encode categorical columns numerically before calling this measurement.
- Remove or impute missing values before scoring.
- Use a stable preprocessing pipeline when comparing MI across experiments.
- Inspect the raw per-feature scores if feature-level ranking matters more than
  a single aggregate summary.

---

## Package Boundary

### What It Owns

`swarmauri_measurement_mutualinformation` is located in `community` and owns mutual-information feature screening measurement for Swarmauri classification datasets using scikit-learn. Source-declared APIs include `MutualInformationMeasurement`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_measurement_mutualinformation`.

Source-declared exports or types: `MutualInformationMeasurement`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.measurements` → `MutualInformationMeasurement` → `swarmauri_measurement_mutualinformation.MutualInformationMeasurement:MutualInformationMeasurement`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_measurement_mutualinformation` are `scikit-learn`, `pandas`, `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_measurement_mutualinformation` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_measurement_mutualinformation`, use the source-declared public interfaces (`MutualInformationMeasurement`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_measurement_mutualinformation` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_measurement_mutualinformation`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py). The `swarmauri_measurement_mutualinformation` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_measurement_mutualinformation` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_measurement_mutualinformation` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for mutual-information feature screening measurement for Swarmauri classification datasets using scikit-learn.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_measurement_mutualinformation` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What input does this measurement expect?**
> A Pandas `DataFrame` plus the name of the target column.

> **What does it return?**
> A single float: the mean of the per-feature mutual-information scores
> produced by `mutual_info_classif`.

> **Does it return one score per feature?**
> No. This component averages the feature scores. If you need per-feature
> values, call `mutual_info_classif` directly.

> **What units are the underlying scores in?**
> Scikit-learn documents `mutual_info_classif` outputs in natural-log units.

### Why

**Why select this package?** `swarmauri_measurement_mutualinformation` provides mutual-information feature screening measurement for Swarmauri classification datasets using scikit-learn; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_measurement_mutualinformation`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/swarmauri_measurement_mutualinformation/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_measurement_mutualinformation` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [scikit-learn `mutual_info_classif` docs](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_classif.html)
- [Pandas documentation](https://pandas.pydata.org/docs/)

### Related Packages

- [swarmauri_measurement_tokencountestimator](https://pypi.org/project/swarmauri_measurement_tokencountestimator/)
- [swarmauri_metric_hamming](https://pypi.org/project/swarmauri_metric_hamming/)
- [swarmauri_measurement_mutualinformation](https://pypi.org/project/swarmauri_measurement_mutualinformation/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_measurement_mutualinformation](https://pypi.org/project/swarmauri_measurement_mutualinformation/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_measurement_mutualinformation`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_measurement_mutualinformation` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_measurement_mutualinformation` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_measurement_mutualinformation` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_measurement_mutualinformation` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_measurement_mutualinformation/NOTICE) for attribution.
<!-- readme-standards:end notices -->
