# swarmauri_tool_scrollfile

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_scrollfile</strong></p>
<p align="center">Bounded UTF-8 file navigation tool for Swarmauri agents and workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img alt="pypi: swarmauri_tool_scrollfile unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_tool_scrollfile%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_scrollfile/"><img alt="pypi downloads: swarmauri_tool_scrollfile: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_tool_scrollfile%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/README.md"><img alt="README hits: swarmauri_tool_scrollfile" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_scrollfile/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_scrollfile` gives agents and workflows a bounded way to inspect
large UTF-8 text files. It returns numbered lines together with stable previous
and next page positions, avoiding full-file output.

### Why This Package

`swarmauri_tool_scrollfile` isolates this responsibility: Bounded UTF-8 file navigation tool for Swarmauri agents and workflows. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py) exposes `ScrollFileTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_scrollfile` when your integration needs bounded UTF-8 file navigation tool for Swarmauri agents and workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Restricts reads to service-configured filesystem roots by default.
- Rejects symlinks unless the service owner explicitly opts in.
- Caps page size, scanned lines and bytes, individual-line size, elapsed
  time, and returned bytes.
- Navigates up or down using one-based line anchors.
- Returns line numbers and explicit previous/next page positions.
- Clamps an anchor beyond EOF to the final available page.
- Validates paths and navigation arguments before reading.
- Registers as a `swarmauri.tools` entry point.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_tool_scrollfile` owns bounded UTF-8 file navigation tool for Swarmauri agents and workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml) declares runtime dependencies including `pydantic`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_scrollfile
```

```bash
pip install swarmauri_tool_scrollfile
```

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_tool_scrollfile` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_tool_scrollfile` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_tool_scrollfile` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_tool_scrollfile
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_tool_scrollfile import ScrollFileTool

tool = ScrollFileTool(allowed_roots=[str(Path("logs").resolve())])
first_page = tool("logs/application.log")

if first_page["has_next"]:
    second_page = tool(
        "logs/application.log",
        start_line=first_page["next_start_line"],
        page_size=first_page["page_size"],
        direction="down",
    )
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_scrollfile` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_tool_scrollfile import ScrollFileTool

tool = ScrollFileTool(allowed_roots=[str(Path("logs").resolve())])
first_page = tool("logs/application.log")

if first_page["has_next"]:
    second_page = tool(
        "logs/application.log",
        start_line=first_page["next_start_line"],
        page_size=first_page["page_size"],
        direction="down",
    )
```
<!-- readme-standards:end example.usage -->

An upward request treats `start_line` as the current page anchor and returns
the preceding page:

```python
previous_page = tool(
    "logs/application.log",
    start_line=second_page["start_line"],
    page_size=second_page["page_size"],
    direction="up",
)
```

Each result contains `lines`, `start_line`, `end_line`, `page_size`,
`has_previous`, `has_next`, `previous_start_line`, and `next_start_line`.

### Configuration

Configure `swarmauri_tool_scrollfile` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_scrollfile` source raises `NotADirectoryError`, `OSError`, `PermissionError`, `ValueError`, `ctypes.WinError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tool_scrollfile` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ScrollFileTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_scrollfile` is located in `community` and owns bounded UTF-8 file navigation tool for Swarmauri agents and workflows. Source-declared APIs include `ScrollFileTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_scrollfile`.

Source-declared exports or types: `ScrollFileTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `ScrollFileTool` → `swarmauri_tool_scrollfile:ScrollFileTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_scrollfile` are `pydantic`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_scrollfile` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_scrollfile`, use the source-declared public interfaces (`ScrollFileTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_scrollfile` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_scrollfile`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

`file_path` is agent-controlled, but filesystem policy is not. The service
owner configures `allowed_roots` when creating the tool; requested paths are
canonically resolved and must remain inside one of those roots. Paths
containing symlinks are rejected by default, and the resolved target must be a
regular file.

```python
tool = ScrollFileTool(
    allowed_roots=["/srv/application-logs", "/srv/reports"],
)
```

The default root is the process working directory. Set `allow_symlinks=True`
only when following symlinks is part of the trusted service configuration.
`allow_unrestricted_paths=True` is a privileged opt-in that disables root
containment; use it only when the process already runs in a least-privilege
filesystem sandbox.

Each call enforces service-owned limits: at most 100 returned lines, 100,000
scanned lines, 8 MiB scanned data, 64 KiB per line, 256 KiB returned content,
and two seconds of file-reading time. Exceeding a limit raises `ValueError`
rather than returning a partial or ambiguous page.

### Compatibility

This source version of `swarmauri_tool_scrollfile` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_scrollfile` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_ScrollFileTool.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/tests/unit/test_ScrollFileTool.py)
- [tests/unit/test_windows_filesystem.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/tests/unit/test_windows_filesystem.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_scrollfile` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tool_scrollfile` provides bounded UTF-8 file navigation tool for Swarmauri agents and workflows; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_scrollfile`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_scrollfile` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/swarmauri_tool_scrollfile/_filesystem.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml) provide the supporting context for `swarmauri_tool_scrollfile`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_scrollfile](https://pypi.org/project/swarmauri_tool_scrollfile/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_scrollfile`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_tool_scrollfile` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Workflow Integration**

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_scrollfile import ScrollFileTool

tools = ToolCollection(
    tools=[ScrollFileTool(allowed_roots=["/srv/application-logs"])]
)
```

**Performance**

The tool streams from the start of the file to the requested page and holds at
most one page plus one lookahead line in memory, subject to the limits above.
Memory use is `O(page_size)`; runtime is `O(start_line + page_size)` for a
stateless request.

**Descriptor-based opening and page boundaries**

Where Linux `openat2` is available, lookups use beneath-root resolution.
If the syscall is unavailable, the POSIX fallback opens a single child of
the trusted root with a no-follow lookup. Nested file lookups fail
with `ENOTSUP`. Policy denials such as `EPERM` or `EACCES` are returned as
errors, including when opening the configured root.

The service must control the configured root, its ancestors, and mount
configuration. A root handle identifies the directory opened by the tool.
Filesystem permissions still govern concurrent changes to opened objects.

`allow_symlinks=True` requires Linux `openat2` and permits only relative links
whose complete resolution stays beneath the selected root. Absolute links,
root escapes, and magic links are rejected. This intentionally narrows the old
opt-in. `allow_unrestricted_paths=True` anchors at the filesystem root; it does
not independently enable symlink following. Configured root paths cannot
contain symlinks or parent traversal.

Opened handles retain inode identity if directories are renamed. This prevents
symlink substitution from redirecting a read, but does not freeze file contents
or prevent another actor from moving an opened directory. Services must control
permissions on their trees.

The returned-content budget applies to the page actually returned, including
EOF fallback. The preceding rolling buffer is bounded separately by page size
and individual-line limits; large earlier lines no longer reject a small later
page merely because they exceed the return budget. A one-byte lookahead detects
the next page without decoding or line-validating its contents. That probe is
still charged against scanned-line and scanned-byte limits. Time checks remain
cooperative and cannot interrupt a filesystem syscall already blocked in the
kernel.

**Windows filesystem support**

On Windows the backend opens the local drive by its volume identity and
opens each component relative to a held directory handle. It rejects junctions
and other reparse points and does not accept UNC or device paths, alternate data
streams, or ambiguous trailing dots or spaces, or reserved DOS basenames. Ancestors are
opened for traversal without requiring listing access. Volume and directory handles
deny delete sharing during traversal. Returned paths are descriptive snapshots.
Confined reads check the opened file and reject files with multiple
hard links. Filesystem permissions govern concurrent changes to file contents.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_scrollfile` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_scrollfile` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_scrollfile` source version is `0.1.0`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/LICENSE).
<!-- readme-standards:end license -->

This package is licensed under Apache-2.0.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_scrollfile/NOTICE) for attribution.
<!-- readme-standards:end notices -->
