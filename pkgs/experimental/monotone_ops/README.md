![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/monotone-ops/">
        <img src="https://img.shields.io/pypi/v/monotone-ops?label=monotone-ops&color=green" alt="PyPI - monotone-ops"/>
    </a>
    <a href="https://pepy.tech/project/monotone-ops/">
        <img src="https://static.pepy.tech/badge/monotone-ops/month" alt="PyPI - Downloads"/>
    </a>
    <a href="https://pypi.org/project/monotone-ops/">
        <img src="https://img.shields.io/pypi/pyversions/monotone-ops" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/monotone-ops/">
        <img src="https://img.shields.io/pypi/l/monotone-ops" alt="PyPI - License"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/monotone_ops/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/monotone_ops.svg"/>
    </a>
</p>

# monotone-ops

A typed Python catalog of monotone operators for deterministic aggregation, evidence rollups,
CRDT state joins, abstract interpretation, positive relational/dataflow rules, semiring path
problems, information lattices, and security/risk labels.

The package is intentionally small and dependency-free at runtime. It provides reusable
operators for experiments that need explicit order semantics, deterministic joins, finite law
checks, or fixpoint-style closure.

`monotone-ops` supports Python 3.10 through 3.12.

## Features

- Defines typed unary, binary, and order protocols for monotone operator experiments.
- Includes finite law checks for associativity, commutativity, idempotence, and monotonicity.
- Covers Boolean, numeric, ordering, collection, sequence, information, interval, graph,
  relational, semiring, probability, evidence, CRDT, security, and Galois-style domains.
- Provides examples for evidence rollups and semiring path problems.
- Ships `py.typed` so downstream packages can type-check imports from `monotone_ops`.

## Installation

### uv

```bash
uv add monotone-ops
```

### pip

```bash
pip install monotone-ops
```

## Usage

The package module is `monotone_ops`.

```python
from monotone_ops.core import fold
from monotone_ops.collections import set_union
from monotone_ops.numeric import saturating_sum

facts = fold(set_union, [frozenset({"a"}), frozenset({"b"})])
score = fold(saturating_sum(10), [3, 4, 9])

assert facts == frozenset({"a", "b"})
assert score == 10
```

## Development

```bash
uv run --directory pkgs --package monotone-ops ruff format experimental/monotone_ops
uv run --directory pkgs --package monotone-ops ruff check experimental/monotone_ops --fix
uv run --directory pkgs --package monotone-ops pytest experimental/monotone_ops/tests
```

## Operator categories

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

## Design rule

An operator in this package is included when it is monotone under an explicit order. Operators
that are also associative, commutative, and idempotent are suitable for order-independent
streaming merges. Operators such as nonnegative sum or logaddexp are monotone and associative
mathematically, but not idempotent; use them for evidence accumulation rather than CRDT-style
state joins.

Clamping operators normalize state. For example, `capped_max(Bounds(0, 1))` is idempotent on
already-clamped values; outside that domain it first maps values into the bounded lattice.

## Research anchors

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
