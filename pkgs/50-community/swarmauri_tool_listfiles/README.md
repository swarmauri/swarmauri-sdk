# swarmauri_tool_listfiles

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_listfiles</strong></p>
<p align="center">Swarmauri tool for listing the files and directories directly inside a folder, with optional absolute paths.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_listfiles/"><img alt="pypi: swarmauri_tool_listfiles" src="https://img.shields.io/pypi/v/swarmauri_tool_listfiles"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml"><img alt="Source version: 0.1.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_listfiles/"><img alt="Monthly PyPI downloads: swarmauri_tool_listfiles" src="https://img.shields.io/pypi/dm/swarmauri_tool_listfiles"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/README.md"><img alt="README hits: swarmauri_tool_listfiles" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_listfiles/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_listfiles` lists what is directly inside a folder: files and
directories, sorted by name, with an optional absolute path for each entry. It
does not recurse, so a listing stays cheap no matter how deep the tree is.

### Why This Package

`swarmauri_tool_listfiles` isolates this responsibility: Swarmauri tool for listing the files and directories directly inside a folder, with optional absolute paths. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py) exposes `ListFilesTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_listfiles` when your integration needs swarmauri tool for listing the files and directories directly inside a folder, with optional absolute paths. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Lists files and directories** in a single call, sorted case-insensitively.
- **Marks directories** with `is_dir`, so a caller never has to guess.
- **Optional absolute paths** via `full_paths=True`; names only by default.
- **Does not recurse.** Deep trees cannot turn a listing into a full scan.
- **Reports problems instead of raising.** A missing path, a path that is a
  file, and an unreadable directory all come back as a structured result.
- **Expands `~`** so home-relative paths work without extra handling.

### Non-Goals

`swarmauri_tool_listfiles` owns swarmauri tool for listing the files and directories directly inside a folder, with optional absolute paths. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
# With uv
uv add swarmauri_tool_listfiles

# With pip
pip install swarmauri_tool_listfiles
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_listfiles
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_listfiles
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_listfiles
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_tool_listfiles import ListFilesTool

# Use a directory that exists; the tool lists what is there and does not
# create anything.
Path("/tmp/project").mkdir(parents=True, exist_ok=True)
Path("/tmp/project/README.md").write_text("x", encoding="utf-8")
Path("/tmp/project/src").mkdir(exist_ok=True)

tool = ListFilesTool(allowed_roots=["/tmp/project"])

result = tool(path="/tmp/project")
# {
#   "path": "/tmp/project",
#   "count": 2,
#   "entries": [
#     {"name": "README.md", "is_dir": False},
#     {"name": "src", "is_dir": True},
#   ],
# }

result = tool(path="/tmp/project", full_paths=True)
# {"name": "README.md", "is_dir": False, "path": "/tmp/project/README.md"}
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_listfiles` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_tool_listfiles import ListFilesTool

# Use a directory that exists; the tool lists what is there and does not
# create anything.
Path("/tmp/project").mkdir(parents=True, exist_ok=True)
Path("/tmp/project/README.md").write_text("x", encoding="utf-8")
Path("/tmp/project/src").mkdir(exist_ok=True)

tool = ListFilesTool(allowed_roots=["/tmp/project"])

result = tool(path="/tmp/project")
# {
#   "path": "/tmp/project",
#   "count": 2,
#   "entries": [
#     {"name": "README.md", "is_dir": False},
#     {"name": "src", "is_dir": True},
#   ],
# }

result = tool(path="/tmp/project", full_paths=True)
# {"name": "README.md", "is_dir": False, "path": "/tmp/project/README.md"}
```
<!-- readme-standards:end example.usage -->

**Result keys**

| Key | Type | Meaning |
| --- | --- | --- |
| `path` | `str` | Resolved directory that was listed |
| `count` | `int` | Number of entries |
| `entries` | `list` | `{"name", "is_dir"}`, plus `"path"` when `full_paths` is set |
| `error` | `str` | Present only when the directory could not be listed |

### Configuration

Configure `swarmauri_tool_listfiles` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_listfiles` source raises `NotADirectoryError`, `OSError`, `PermissionError`, `ValueError`, `ctypes.WinError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tool_listfiles` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ListFilesTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_listfiles` is located in `community` and owns swarmauri tool for listing the files and directories directly inside a folder, with optional absolute paths. Source-declared APIs include `ListFilesTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_listfiles`.

Source-declared exports or types: `ListFilesTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `ListFilesTool` → `swarmauri_tool_listfiles.ListFilesTool:ListFilesTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_listfiles` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_listfiles` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_listfiles`, use the source-declared public interfaces (`ListFilesTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_listfiles` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_listfiles`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py). The `swarmauri_tool_listfiles` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_listfiles` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_listfiles` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_boundaries.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/tests/unit/test_boundaries.py)
- [tests/unit/test_windows_filesystem.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/tests/unit/test_windows_filesystem.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_listfiles` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **Does it recurse?**
> No. Use a search tool for that. A listing of a huge tree stays a listing of
> one level.

> **Why sort by name rather than directories first?**
> A stable, predictable order matters more than grouping; callers that care
> filter on `is_dir`.

> **Are symlinks followed?**
> Symlink entries are listed without dereferencing their targets and report
> `is_dir: False`. Requested directory paths may not contain symlinks.

### Why

**Why select this package?** `swarmauri_tool_listfiles` provides swarmauri tool for listing the files and directories directly inside a folder, with optional absolute paths; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_listfiles`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_listfiles` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/swarmauri_tool_listfiles/_filesystem.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml) provide the supporting context for `swarmauri_tool_listfiles`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_listfiles](https://pypi.org/project/swarmauri_tool_listfiles/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_listfiles`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_listfiles` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Expected workflows**

- **Survey before acting.** An agent lists a folder, then chooses a file to
  read or edit.
- **Confirm a write target.** List the parent directory to check that a name is
  free before creating a file.
- **Fail safely.** Callers check for `error` rather than wrapping the call in
  `try`, because refusals are values, not exceptions.

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
errors, including when opening the configured root. Listing the configured root itself is also supported.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

On POSIX, a scanned descendant is checked again by identity before results
are returned. A detected move or replacement causes the scan to fail.

Service-owned defaults cap scans at 100,000 entries, results at 10,000, returned
JSON at 1 MiB, and elapsed scanning at two seconds. These constructor fields
(`max_scanned_entries`, `max_results`, `max_return_bytes`,
`max_elapsed_seconds`) are not agent-call parameters. Limit exhaustion returns
an explicit error and an empty result rather than successful partial data.
Time checks are cooperative and cannot interrupt a filesystem call blocked in
the kernel. Success responses obey `max_return_bytes`. Error responses truncate
echoed input and diagnostics to at most 4 KiB, or the configured byte budget
when smaller, with a 256-byte minimum to preserve a structured error envelope.

Symlinks are listed as entries with `is_dir=False`, including links to
directories. Classification never dereferences the target. Full paths name the
listed entries, rather than their targets. Sorting uses the original name to
break case-insensitive ties deterministically.

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

Changes to `swarmauri_tool_listfiles` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_listfiles` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_listfiles` source version is `0.1.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_listfiles/NOTICE) for attribution.
<!-- readme-standards:end notices -->
