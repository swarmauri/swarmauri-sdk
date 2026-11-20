# swarmauri_tool_findfile

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_findfile</strong></p>
<p align="center">Swarmauri tool for finding files under a directory by shell-style wildcard name matching, case-insensitively, with optional recursion.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_findfile/"><img alt="pypi: swarmauri_tool_findfile" src="https://img.shields.io/pypi/v/swarmauri_tool_findfile"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml"><img alt="Source version: 0.1.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_findfile/"><img alt="Monthly PyPI downloads: swarmauri_tool_findfile" src="https://img.shields.io/pypi/dm/swarmauri_tool_findfile"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/README.md"><img alt="README hits: swarmauri_tool_findfile" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_findfile/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_findfile` searches a directory for files whose name matches a
shell-style wildcard, case-insensitively, with optional recursion into
subdirectories.

### Why This Package

`swarmauri_tool_findfile` isolates this responsibility: Swarmauri tool for finding files under a directory by shell-style wildcard name matching, case-insensitively, with optional recursion. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py) exposes `FindFileTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_findfile` when your integration needs swarmauri tool for finding files under a directory by shell-style wildcard name matching, case-insensitively, with optional recursion. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Wildcard matching** with `*`, `?` and `[seq]`, matched against the file
  name rather than the whole path.
- **Case-insensitive** on every platform, so `*.LOG` and `*.log` behave the
  same wherever the code runs.
- **Optional recursion** via `recursive=True`; the default checks one level.
- **Never follows symbolic links**, so a link cycle cannot make the walk run
  forever.
- **Returns files, not directories.** This answers "which files match", not
  "what is here".
- **Reports problems instead of raising**, with the same result shape in every
  case.

### Non-Goals

`swarmauri_tool_findfile` owns swarmauri tool for finding files under a directory by shell-style wildcard name matching, case-insensitively, with optional recursion. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
# With uv
uv add swarmauri_tool_findfile

# With pip
pip install swarmauri_tool_findfile
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_findfile
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_findfile
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_findfile
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_tool_findfile import FindFileTool

# Build a small tree so the example is reproducible.
Path("/tmp/logs/archive").mkdir(parents=True, exist_ok=True)
Path("/tmp/logs/app.log").write_text("x", encoding="utf-8")
Path("/tmp/logs/archive/old.log").write_text("x", encoding="utf-8")

tool = FindFileTool(allowed_roots=["/tmp/logs"])

tool(path="/tmp/logs", pattern="*.log")
# {"path": "/tmp/logs", "pattern": "*.log", "count": 1,
#  "matches": ["/tmp/logs/app.log"]}

tool(path="/tmp/logs", pattern="*.log", recursive=True)
# {"count": 2, "matches": ["/tmp/logs/app.log", "/tmp/logs/archive/old.log"]}
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_findfile` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_tool_findfile import FindFileTool

# Build a small tree so the example is reproducible.
Path("/tmp/logs/archive").mkdir(parents=True, exist_ok=True)
Path("/tmp/logs/app.log").write_text("x", encoding="utf-8")
Path("/tmp/logs/archive/old.log").write_text("x", encoding="utf-8")

tool = FindFileTool(allowed_roots=["/tmp/logs"])

tool(path="/tmp/logs", pattern="*.log")
# {"path": "/tmp/logs", "pattern": "*.log", "count": 1,
#  "matches": ["/tmp/logs/app.log"]}

tool(path="/tmp/logs", pattern="*.log", recursive=True)
# {"count": 2, "matches": ["/tmp/logs/app.log", "/tmp/logs/archive/old.log"]}
```
<!-- readme-standards:end example.usage -->

**Result keys**

| Key | Type | Meaning |
| --- | --- | --- |
| `path` | `str` | Root directory that was searched |
| `pattern` | `str` | Pattern as supplied |
| `count` | `int` | Number of matching files |
| `matches` | `list[str]` | Absolute paths, sorted |
| `error` | `str` | Present only when the search could not run |

### Configuration

Configure `swarmauri_tool_findfile` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_findfile` source raises `NotADirectoryError`, `OSError`, `PermissionError`, `ValueError`, `ctypes.WinError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tool_findfile` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `FindFileTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_findfile` is located in `community` and owns swarmauri tool for finding files under a directory by shell-style wildcard name matching, case-insensitively, with optional recursion. Source-declared APIs include `FindFileTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_findfile`.

Source-declared exports or types: `FindFileTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `FindFileTool` → `swarmauri_tool_findfile.FindFileTool:FindFileTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_findfile` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_findfile` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_findfile`, use the source-declared public interfaces (`FindFileTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_findfile` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_findfile`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py). The `swarmauri_tool_findfile` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_findfile` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_findfile` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_boundaries.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/tests/unit/test_boundaries.py)
- [tests/unit/test_invalid_patterns.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/tests/unit/test_invalid_patterns.py)
- [tests/unit/test_windows_filesystem.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/tests/unit/test_windows_filesystem.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_findfile` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **Why case-insensitive by default rather than by flag?**
> The same tree yields different results on macOS and Linux otherwise, and a
> search that silently misses `Report.PDF` is the failure mode that hurts.

> **Does it follow symlinks?**
> No. Links are never traversed, so a directory that links back to its parent
> cannot produce an infinite walk.

> **Why does it only return files?**
> Directories are a different question with a different tool; mixing them makes
> every caller filter the result.

### Why

**Why select this package?** `swarmauri_tool_findfile` provides swarmauri tool for finding files under a directory by shell-style wildcard name matching, case-insensitively, with optional recursion; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_findfile`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_findfile` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/swarmauri_tool_findfile/_filesystem.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml) provide the supporting context for `swarmauri_tool_findfile`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_findfile](https://pypi.org/project/swarmauri_tool_findfile/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_findfile`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_tool_findfile` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Expected workflows**

- **Locate by extension.** `*.csv` before loading a dataset.
- **Find a report by convention.** `report?.txt` or `2026-*.pdf`.
- **Scope a bulk action.** Gather matches, then act on the list.

**Trusted roots and resource limits**

Configure `allowed_roots` on the tool from trusted service code. The default is
its construction-time working directory. Relative requests use the call-time
working directory and must still lie beneath a configured root. Empty roots
reject every request. Roots must be absolute; parent traversal and symlinks in
requested directory paths or root paths are rejected.

Where Linux `openat2` is available, lookups use beneath-root resolution.
If the syscall is unavailable, the POSIX fallback opens a single child of
the trusted root with a no-follow lookup. Nested directory lookups fail
with `ENOTSUP`. Policy denials such as `EPERM` or `EACCES` are returned as
errors, including when opening the configured root. Searching from the configured root
or a direct child is supported as long as the search need not open a
directory more than one level below the configured root. A search that
needs to open a deeper directory returns an error and discards partial
results.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

On POSIX, recursive directories are opened from the original root handle and
checked again by identity after enumeration. A detected move or replacement causes the scan to fail.

Service-owned defaults cap scans at 100,000 entries, results at 10,000, returned
JSON at 1 MiB, and elapsed scanning at two seconds. These constructor fields
(`max_scanned_entries`, `max_results`, `max_return_bytes`,
`max_elapsed_seconds`) are not agent-call parameters. Limit exhaustion returns
an explicit error and an empty result rather than successful partial data.
Time checks are cooperative and cannot interrupt a filesystem call blocked in
the kernel. Success responses obey `max_return_bytes`. Error responses truncate
echoed input and diagnostics to at most 4 KiB, or the configured byte budget
when smaller, with a 256-byte minimum to preserve a structured error envelope.

Both search modes return regular files only: symlinks, FIFOs, sockets, and other
special entries are excluded. Recursive directory opens are descriptor-relative
and never follow symlinks. `max_depth` defaults to 64 and
`max_pattern_length` to 1,024 characters; both are service-owned limits. Filename
matching remains case-insensitive, and results remain sorted absolute paths.

**Windows filesystem support**

On Windows the backend opens the local drive by its volume identity and
opens each component relative to a held directory handle. It rejects junctions
and other reparse points and does not accept UNC or device paths, alternate data
streams, or ambiguous trailing dots or spaces, or reserved DOS basenames. Ancestors are
opened for traversal. Only a directory being enumerated requires listing access.
Volume and directory handles
deny delete sharing during traversal. Returned paths are descriptive snapshots.
Entries with names that ordinary Windows paths cannot represent are omitted.
A listed pathname conveys no permission to open its contents.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_findfile` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_findfile` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_findfile` source version is `0.1.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_findfile/NOTICE) for attribution.
<!-- readme-standards:end notices -->
