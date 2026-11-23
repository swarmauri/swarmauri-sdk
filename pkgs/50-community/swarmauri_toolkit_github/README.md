# swarmauri_toolkit_github

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_toolkit_github</strong></p>
<p align="center">Github Toolkit</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_toolkit_github/"><img alt="pypi: swarmauri_toolkit_github" src="https://img.shields.io/pypi/v/swarmauri_toolkit_github?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_toolkit_github/"><img alt="Monthly PyPI downloads: swarmauri_toolkit_github" src="https://img.shields.io/pypi/dm/swarmauri_toolkit_github?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/README.md"><img alt="README hits: swarmauri_toolkit_github" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_toolkit_github/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A Swarmauri toolkit that wraps PyGithub behind Swarmauri?s agent/tool abstractions. Authenticate once and gain access to repository, issue, pull request, branch, and commit helpers?ready for scripted automation or conversational agents.

- Creates a shared GitHub client so every tool call reuses the same token and rate-limit state.
- Normalizes responses into dictionaries so downstream logic can inspect status messages or raw PyGithub payloads.
- Covers common actions (create/list/update/delete) while staying extensible via the `action` parameter on each tool.

### Why This Package

`swarmauri_toolkit_github` isolates this responsibility: Github Toolkit. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py) exposes `GithubBranchTool`, `GithubCommitTool`, `GithubIssueTool`, `GithubPRTool`, `GithubRepoTool`, `GithubToolkit`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_toolkit_github` when your integration needs github Toolkit. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `GithubBranchTool`: declared in swarmauri_toolkit_github/GithubBranchTool.py
- `GithubCommitTool`: declared in swarmauri_toolkit_github/GithubCommitTool.py
- `GithubIssueTool`: declared in swarmauri_toolkit_github/GithubIssueTool.py
- `GithubPRTool`: declared in swarmauri_toolkit_github/GithubPRTool.py
- `GithubRepoTool`: declared in swarmauri_toolkit_github/GithubRepoTool.py
- `GithubToolkit`: declared in swarmauri_toolkit_github/GithubToolkit.py

### Non-Goals

`swarmauri_toolkit_github` owns github Toolkit. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Python 3.10 ? 3.13.
- GitHub personal access token (classic or fine-grained) with the scopes your workflow requires. Store it in an environment variable such as `GITHUB_TOKEN`.
- Runtime dependencies (`PyGithub`, `python-dotenv`, and the Swarmauri base/standard packages) install automatically with the toolkit.

### Installation

Choose any of the supported packaging flows; each command resolves transitive dependencies.

**pip**

```bash
pip install swarmauri_toolkit_github
```

**Poetry**

```bash
poetry add swarmauri_toolkit_github
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_toolkit_github

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_toolkit_github
```

> Tip: `python-dotenv` is imported automatically?drop your token into a local `.env` file (`GITHUB_TOKEN=ghp_...`) for quick experimentation.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_toolkit_github
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_toolkit_github
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_toolkit_github
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

Each sub-tool accepts an `action` argument (see PyGithub docs for additional options) and returns a dictionary keyed by that action for ergonomic unpacking.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/docs/readme/quick_start.py).

```python
import os
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])

# List repositories for the authenticated user
repos = toolkit.github_repo_tool(action="list_repos")
print(repos["list_repos"])

# Open a tracking issue
issue = toolkit.github_issue_tool(
    action="create_issue",
    repo_name="owner/example",
    title="Investigate flaky tests",
    body="Logs: https://gist.github.com/...",
)
print(issue["create_issue"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_toolkit_github` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/docs/readme/usage.py).

```python
import os
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])

# Create a release branch
toolkit.github_branch_tool(
    action="create_branch",
    repo_name="owner/service",
    new_branch="release/v1.4.0",
    source_branch="master",
)

# Cut a changelog commit
toolkit.github_commit_tool(
    action="create_file",
    repo_name="owner/service",
    path="CHANGELOG.md",
    message="Add release notes",
    content="### v1.4.0\n- New features...",
    branch="release/v1.4.0",
)
```
<!-- readme-standards:end example.usage -->

**Automate Release Housekeeping**


**Drive GitHub From a Swarmauri Agent**

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])
registry = ToolRegistry()
registry.register(toolkit.github_issue_tool)
registry.register(toolkit.github_pr_tool)

agent = Agent(tool_registry=registry)
response = agent.run(HumanMessage(content="Open a PR from feature/auth to master"))
print(response)
```

Enable conversational workflows that translate natural-language requests into GitHub mutations.

**Triage Issues Nightly**

```python
from datetime import datetime, timedelta
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])
cutoff = datetime.utcnow() - timedelta(days=7)

issues = toolkit.github_issue_tool(
    action="list",
    repo_name="owner/product",
    state="open"
)["list"]

stale = [issue for issue in issues if issue.updated_at < cutoff]
for issue in stale:
    toolkit.github_issue_tool(
        action="create_comment",
        repo_name="owner/product",
        number=issue.number,
        body="Ping! Any update in the last week?"
    )
```

Keep a backlog tidy by automatically nudging stale tickets.

### Configuration

Configure `swarmauri_toolkit_github` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_toolkit_github` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_toolkit_github` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `GithubBranchTool`, `GithubCommitTool`, `GithubIssueTool`, `GithubPRTool`, `GithubRepoTool`, `GithubToolkit`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_toolkit_github` is located in `community` and owns github Toolkit. Source-declared APIs include `GithubBranchTool`, `GithubCommitTool`, `GithubIssueTool`, `GithubPRTool`, `GithubRepoTool`, `GithubToolkit`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_toolkit_github`.

Source-declared exports or types: `GithubBranchTool`, `GithubCommitTool`, `GithubIssueTool`, `GithubPRTool`, `GithubRepoTool`, `GithubToolkit`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.toolkits` → `GithubToolkit` → `swarmauri_toolkit_github.GithubToolkit:GithubToolkit`
- `swarmauri.tools` → `GithubBranchTool` → `swarmauri_toolkit_github.GithubBranchTool:GithubBranchTool`
- `swarmauri.tools` → `GithubCommitTool` → `swarmauri_toolkit_github.GithubCommitTool:GithubCommitTool`
- `swarmauri.tools` → `GithubIssueTool` → `swarmauri_toolkit_github.GithubIssueTool:GithubIssueTool`
- `swarmauri.tools` → `GithubPRTool` → `swarmauri_toolkit_github.GithubPRTool:GithubPRTool`
- `swarmauri.tools` → `GithubRepoTool` → `swarmauri_toolkit_github.GithubRepoTool:GithubRepoTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_toolkit_github` are `pygithub`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_toolkit_github` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_toolkit_github`, use the source-declared public interfaces (`GithubBranchTool`, `GithubCommitTool`, `GithubIssueTool`, `GithubPRTool`, `GithubRepoTool`, `GithubToolkit`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_toolkit_github` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_toolkit_github`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py). The `swarmauri_toolkit_github` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_toolkit_github` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_toolkit_github` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for github Toolkit.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_toolkit_github` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_toolkit_github` provides github Toolkit; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_toolkit_github`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_toolkit_github` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/swarmauri_toolkit_github/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml) provide the supporting context for `swarmauri_toolkit_github`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_toolkit_github](https://pypi.org/project/swarmauri_toolkit_github/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_toolkit_github`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_toolkit_github` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Troubleshooting**

- **`ValueError: Invalid Token or Missing api_token`** ? Pass the token explicitly (`GithubToolkit(api_token=...)`) or export `GITHUB_TOKEN` before instantiating the toolkit.
- **PyGithub exception messages** ? Most actions bubble up PyGithub errors verbatim (permission issues, missing branches, etc.). Inspect the text in the returned string to resolve scope or naming problems.
- **GitHub rate limits** ? PyGithub tracks remaining requests; consider batching actions or sleeping when `Github.get_rate_limit()` indicates low headroom.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_toolkit_github` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_toolkit_github` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_toolkit_github` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/LICENSE).
<!-- readme-standards:end license -->

`swarmauri_toolkit_github` is released under the Apache 2.0 License. See `LICENSE` for full details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_toolkit_github/NOTICE) for attribution.
<!-- readme-standards:end notices -->
