# swarmauri_tool_createfile

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_createfile</strong></p>
<p align="center">Swarmauri tool for creating a new UTF-8 text file at a path, with optional initial content and a refusal to overwrite.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_createfile/"><img alt="pypi: swarmauri_tool_createfile" src="https://img.shields.io/pypi/v/swarmauri_tool_createfile"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml"><img alt="Source version: 0.1.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_createfile/"><img alt="Monthly PyPI downloads: swarmauri_tool_createfile" src="https://img.shields.io/pypi/dm/swarmauri_tool_createfile"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/README.md"><img alt="README hits: swarmauri_tool_createfile" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_createfile/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_createfile` is a Swarmauri tool for creating a new text file at
a given path, optionally with initial content. It is meant for agent workflows
that need to write a generated report, a scaffolded module, a note, or any other
plain-text artifact to disk without shelling out.

### Why This Package

`swarmauri_tool_createfile` isolates this responsibility: Swarmauri tool for creating a new UTF-8 text file at a path, with optional initial content and a refusal to overwrite. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py) exposes `CreateFileTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_createfile` when your integration needs swarmauri tool for creating a new UTF-8 text file at a path, with optional initial content and a refusal to overwrite. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Create a file with content** in a single call, written as UTF-8.
- **Create an empty file** when no content is supplied.
- **Never overwrites.** If anything already exists at the path, the call
  reports it and writes nothing.
- **Reports problems instead of raising.** A missing parent directory, an
  existing file, or an OS-level write failure all come back as a structured
  result, so an agent can read the reason and pick another path.
- **Expands `~`** so home-relative paths work without extra handling.
- **Restricts writes to trusted roots** configured by the service owner.
  Symlinks and parent traversal are rejected.

### Non-Goals

`swarmauri_tool_createfile` owns swarmauri tool for creating a new UTF-8 text file at a path, with optional initial content and a refusal to overwrite. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
# With uv
uv add swarmauri_tool_createfile

# With pip
pip install swarmauri_tool_createfile
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_createfile
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_createfile
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_createfile
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_tool_createfile import CreateFileTool

# The tool does not create parent directories, so make the parent first.
reports = Path.cwd() / "reports"
reports.mkdir(parents=True, exist_ok=True)

tool = CreateFileTool(allowed_roots=[str(reports)])

result = tool(
    path=str(reports / "summary.txt"),
    content="Quarterly summary\n",
)
# {"created": True, "path": ".../reports/summary.txt", "bytes_written": 18}

# Nothing is written when the path is already taken.
result = tool(path=str(reports / "summary.txt"), content="overwrite attempt")
assert result["created"] is False
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_createfile` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_tool_createfile import CreateFileTool

# The tool does not create parent directories, so make the parent first.
reports = Path.cwd() / "reports"
reports.mkdir(parents=True, exist_ok=True)

tool = CreateFileTool(allowed_roots=[str(reports)])

result = tool(
    path=str(reports / "summary.txt"),
    content="Quarterly summary\n",
)
# {"created": True, "path": ".../reports/summary.txt", "bytes_written": 18}

# Nothing is written when the path is already taken.
result = tool(path=str(reports / "summary.txt"), content="overwrite attempt")
assert result["created"] is False
```
<!-- readme-standards:end example.usage -->

**Result keys**

| Key | Type | Meaning |
| --- | --- | --- |
| `created` | `bool` | Whether creation and writing completed successfully |
| `path` | `str` | Absolute expanded destination on valid-path calls; original input on expansion failure |
| `bytes_written` | `int` | Size obtained from the open file descriptor, present only on success |
| `error` | `str` | Human-readable reason, present only on refusal |

### Configuration

Configure `swarmauri_tool_createfile` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_createfile` source raises `FileExistsError`, `NotADirectoryError`, `OSError`, `PermissionError`, `ValueError`, `ctypes.WinError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tool_createfile` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CreateFileTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_createfile` is located in `community` and owns swarmauri tool for creating a new UTF-8 text file at a path, with optional initial content and a refusal to overwrite. Source-declared APIs include `CreateFileTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_createfile`.

Source-declared exports or types: `CreateFileTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `CreateFileTool` → `swarmauri_tool_createfile.CreateFileTool:CreateFileTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_createfile` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_createfile` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_createfile`, use the source-declared public interfaces (`CreateFileTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_createfile` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_createfile`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py). The `swarmauri_tool_createfile` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_createfile` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_createfile` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_windows_filesystem.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/tests/unit/test_windows_filesystem.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_createfile` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **Does it create parent directories?**
> Create the parent directory first. On POSIX, configure the existing parent
> as an allowed root when the service controls that directory and its ancestors.

> **Does it overwrite?**
> Never. There is no overwrite flag by design; delete the file first if that is
> what you mean.

> **Is binary content supported?**
> No. The tool writes text as UTF-8 only.

### Why

**Why select this package?** `swarmauri_tool_createfile` provides swarmauri tool for creating a new UTF-8 text file at a path, with optional initial content and a refusal to overwrite; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_createfile`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_createfile` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/swarmauri_tool_createfile/_paths.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml) provide the supporting context for `swarmauri_tool_createfile`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_createfile](https://pypi.org/project/swarmauri_tool_createfile/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_createfile`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_tool_createfile` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Expected workflows**

- **Write generated output.** An agent produces text and persists it to a path
  chosen by the caller.
- **Scaffold before editing.** Create the file, then let a separate editing tool
  modify it.
- **Fail safely.** Callers check `created` rather than wrapping the call in
  `try`, because refusals are values, not exceptions.

**Filesystem policy and failure behavior**

The service owner configures `allowed_roots` as existing absolute directories.
The default is the working directory at tool construction. This configuration
is not an agent-call parameter. Relative destinations are interpreted against
the working directory at call time and must still lie beneath an allowed root.
An empty root list denies all writes. Existing symlinks anywhere in the root or
destination path are rejected; `..` components are rejected rather than resolved.

On POSIX, the destination must be a direct child of a configured root.
Configure the destination's existing parent as an allowed root only when
the service controls that directory and its ancestors. This avoids
creating through a nested parent that can move outside the root during
lookup. Creation uses one exclusive, no-follow lookup from the root
descriptor. Linux uses `openat2` to open the configured root when
available. If the syscall is unavailable, the tool walks the trusted root
path without following symlinks. Policy denials such as `EPERM` or
`EACCES` are returned as errors.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

UTF-8 encoding is checked before creation. Exclusive creation atomically refuses
existing entries, including dangling symlinks; writing the full content is not an
atomic publication. If an OS write, descriptor-stat, or close operation fails,
`created` is false and the error warns that partial output may remain. The tool
does not unlink the final pathname, because another process may have replaced
it. Service-owned recovery must inspect incomplete output rather than blindly
deleting or retrying at the same pathname.

**Windows filesystem support**

On Windows the backend opens the local drive by its volume identity and
opens each component relative to a held directory handle. It rejects junctions
and other reparse points and does not accept UNC or device paths, alternate data
streams, or ambiguous trailing dots or spaces, or reserved DOS basenames. Ancestors are
opened for traversal without requiring listing access. Volume and directory handles
deny delete sharing during traversal. Returned paths are descriptive snapshots.
Existing entries, including hard links, cannot be overwritten by exclusive
creation.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_createfile` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_createfile` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_createfile` source version is `0.1.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_createfile/NOTICE) for attribution.
<!-- readme-standards:end notices -->
