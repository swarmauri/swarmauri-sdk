# monotone-ops

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>monotone-ops</strong></p>
<p align="center">Research-oriented monotone operator catalog for deterministic aggregation, CRDTs, fixpoints, and algebraic dataflow.</p>
<p align="center">
<a href="https://pypi.org/project/monotone-ops/"><img alt="pypi: monotone-ops" src="https://img.shields.io/pypi/v/monotone-ops"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/monotone-ops/"><img alt="Monthly PyPI downloads: monotone-ops" src="https://img.shields.io/pypi/dm/monotone-ops"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/README.md"><img alt="README hits: monotone-ops" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/70-experimental/monotone_ops/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A typed Python catalog of monotone operators for deterministic aggregation, evidence rollups,
CRDT state joins, abstract interpretation, positive relational/dataflow rules, semiring path
problems, information lattices, and security/risk labels.

The package is intentionally small and dependency-free at runtime. It provides reusable
operators for experiments that need explicit order semantics, deterministic joins, finite law
checks, or fixpoint-style closure.

`monotone-ops` supports Python 3.10 through 3.12.

### Why This Package

`monotone-ops` isolates this responsibility: Research-oriented monotone operator catalog for deterministic aggregation, CRDTs, fixpoints, and algebraic dataflow. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py) exposes `abstract`, `boolean`, `collections`, `core`, `crdt`, `evidence`, `fixedpoint`, `galois`, `graph`, `information`, `intervals`, `laws`, `matrix`, `numeric`, `ordering`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `monotone-ops` when your integration needs research-oriented monotone operator catalog for deterministic aggregation, CRDTs, fixpoints, and algebraic dataflow. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Defines typed unary, binary, and order protocols for monotone operator experiments.
- Includes finite law checks for associativity, commutativity, idempotence, and monotonicity.
- Covers Boolean, numeric, ordering, collection, sequence, information, interval, graph,
  relational, semiring, probability, evidence, CRDT, security, and Galois-style domains.
- Provides examples for evidence rollups and semiring path problems.
- Ships `py.typed` so downstream packages can type-check imports from `monotone_ops`.

### Non-Goals

`monotone-ops` owns research-oriented monotone operator catalog for deterministic aggregation, CRDTs, fixpoints, and algebraic dataflow. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml) declares no direct runtime dependencies. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add monotone-ops
```
<!-- readme-standards:end installation.uv -->

```bash
uv add monotone-ops
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install monotone-ops
```
<!-- readme-standards:end installation.pip -->

```bash
pip install monotone-ops
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add monotone-ops
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/docs/readme/quick_start.py).

```python
from monotone_ops.core import fold
from monotone_ops.collections import set_union
from monotone_ops.numeric import saturating_sum

facts = fold(set_union, [frozenset({"a"}), frozenset({"b"})])
score = fold(saturating_sum(10), [3, 4, 9])

assert facts == frozenset({"a", "b"})
assert score == 10
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `monotone-ops` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/docs/readme/usage.py).

```python
from monotone_ops.core import fold
from monotone_ops.collections import set_union
from monotone_ops.numeric import saturating_sum

facts = fold(set_union, [frozenset({"a"}), frozenset({"b"})])
score = fold(saturating_sum(10), [3, 4, 9])

assert facts == frozenset({"a", "b"})
assert score == 10
```
<!-- readme-standards:end example.usage -->

The package module is `monotone_ops`.

### Configuration

Configure `monotone-ops` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `monotone-ops` source raises `AssertionError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `monotone-ops` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `abstract`, `boolean`, `collections`, `core`, `crdt`, `evidence`, `fixedpoint`, `galois`, `graph`, `information`, `intervals`, `laws`, `matrix`, `numeric`, `ordering`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`monotone-ops` is located in `experimental` and owns research-oriented monotone operator catalog for deterministic aggregation, CRDTs, fixpoints, and algebraic dataflow. Source-declared APIs include `abstract`, `boolean`, `collections`, `core`, `crdt`, `evidence`, `fixedpoint`, `galois`, `graph`, `information`, `intervals`, `laws`, `matrix`, `numeric`, `ordering`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `monotone_ops`.

Source-declared exports or types: `abstract`, `boolean`, `collections`, `core`, `crdt`, `evidence`, `fixedpoint`, `galois`, `graph`, `information`, `intervals`, `laws`, `matrix`, `numeric`, `ordering`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `monotone-ops` are empty in the manifest. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `monotone-ops` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `monotone-ops`, use the source-declared public interfaces (`abstract`, `boolean`, `collections`, `core`, `crdt`, `evidence`, `fixedpoint`, `galois`, `graph`, `information`, `intervals`, `laws`, `matrix`, `numeric`, `ordering`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `monotone-ops` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `monotone-ops`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py). The `monotone-ops` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `monotone-ops` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `monotone-ops` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_core_laws.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/tests/test_core_laws.py)
- [tests/test_domains.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/tests/test_domains.py)
- [tests/test_regressions.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/tests/test_regressions.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `monotone-ops` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `monotone-ops` provides research-oriented monotone operator catalog for deterministic aggregation, CRDTs, fixpoints, and algebraic dataflow; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `monotone-ops`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `monotone-ops` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/src/monotone_ops/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml) provide the supporting context for `monotone-ops`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `monotone-ops` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: monotone-ops](https://pypi.org/project/monotone-ops/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `monotone-ops`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/70-experimental/monotone_ops` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

```bash
uv run --directory pkgs --package monotone-ops ruff format experimental/monotone_ops
uv run --directory pkgs --package monotone-ops ruff check experimental/monotone_ops --fix
uv run --directory pkgs --package monotone-ops pytest experimental/monotone_ops/tests
```

### Notes for Maintainers

**Operator categories**

| Module | Category | Examples |
| --- | --- | --- |
| `core` | protocols, folds, orders | `Binary`, `Leq`, `fold`, `scan`, `dual`, `product_leq` |
| `laws` | finite law checks | associativity, commutativity, idempotence, monotonicity |
| `boolean` | positive Boolean functions | OR, AND, k-of-n, majority, monotone CNF/DNF |
| `numeric` | numeric monotone maps | max, min, nonnegative sum/product, saturation, clamp, positive linear maps |
| `ordering` | order-induced selectors | argmax, argmin, lexicographic max/min, Pareto antichain join |
| `collections` | set/map/tuple/counter/bitset | union, intersection, dict pointwise join/meet, counter max/min |
| `sequence` | prefix/subsequence orders | append, longest common prefix, ordered dedup union, scans |
| `information` | knowledge lattices | unknown/known/conflict join, record joins, provenance support |
| `intervals` | abstract interval domain | hull join, intersection meet, interval arithmetic, widening/narrowing |
| `abstract` | small abstract domains | sign lattice, taint lattice, finite powerset abstraction |
| `fixedpoint` | closure/fixpoint iteration | least fixpoint, inflationary fixpoint, set closure, positive rule closure |
| `galois` | adjunction-derived operators | closure/interior operators, Moore closure, Alexandrov interior |
| `graph` | graph inclusion operators | graph union, reachability, transitive closure, components |
| `relational` | positive relational algebra | union, selection, projection, natural join, positive consequence |
| `semiring` | algebraic path operators | Boolean, tropical, max-plus, max-min, Viterbi, Floyd-Warshall closure |
| `matrix` | entrywise/grid operators | entrywise max/min/add, monotone dilation/erosion |
| `probability` | confidence/evidence scoring | max confidence, noisy-or, logaddexp, bounded evidence sum |
| `evidence` | quorum/certification | quorum state, weighted evidence, claim support, scorecards |
| `crdt` | state-based CRDT joins | G-Set, 2P-Set, G-Counter, PN-Counter, LWW register, OR-Set, vector clock |
| `security` | labels and policy lattices | restrictive decision join, permission bitsets, risk max, trust min |

**Design rule**

An operator in this package is included when it is monotone under an explicit order. Operators
that are also associative, commutative, and idempotent are suitable for order-independent
streaming merges. Operators such as nonnegative sum or logaddexp are monotone and associative
mathematically, but not idempotent; use them for evidence accumulation rather than CRDT-style
state joins.

Clamping operators normalize state. For example, `capped_max(Bounds(0, 1))` is idempotent on
already-clamped values; outside that domain it first maps values into the bounded lattice.

**Research anchors**

This catalog is organized around established monotone structures:

- Lattices, joins, meets, closure/interior operators, and Tarski-style fixed points.
- CRDT state convergence via monotonic semilattices and least-upper-bound merge.
- Abstract interpretation via ordered abstract domains, joins, widenings, and fixpoint approximation.
- Positive relational algebra and Datalog-style immediate-consequence operators.
- Semiring frameworks for generic shortest-distance and algebraic path problems.

Primary references used while shaping the catalog:

- Shapiro et al., *Conflict-Free Replicated Data Types*, 2011.
- Cousot and Cousot, *Abstract Interpretation: A Unified Lattice Model*, POPL 1977.
- Tarski fixed point theorem lecture notes, EPFL/LARA.
- Nutt, *Datalog with Negation*, Foundations of Database Systems lecture notes.
- Mohri, *Semiring Frameworks and Algorithms for Shortest-Distance Problems*.
- Astral `uv` documentation for project and build-backend structure.

---

## Governance

### Ownership and Decision Making

Changes to `monotone-ops` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`monotone-ops` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `monotone-ops` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/monotone_ops/NOTICE) for attribution.
<!-- readme-standards:end notices -->
