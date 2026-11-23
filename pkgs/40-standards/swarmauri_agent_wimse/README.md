# swarmauri_agent_wimse

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_agent_wimse</strong></p>
<p align="center">Run a WIMSE-authenticated research agent with a delegated file read tool.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_wimse/"><img alt="pypi: swarmauri_agent_wimse unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_agent_wimse%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_wimse/"><img alt="pypi downloads: swarmauri_agent_wimse: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_agent_wimse%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/README.md"><img alt="README hits: swarmauri_agent_wimse" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_agent_wimse/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/tests/unit/test_nine_hop_native.py"><img alt="Tests: package tests" src="https://img.shields.io/static/v1?label=Tests&amp;message=package%20tests&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Deployable HTTP endpoints for WIMSE workflow admission, research, and delegated file reads.

### Why This Package

Use the same request-bound identity and delegation checks across an ingress, a research agent, and a file service.

### When to Use

Use this package when a signed workload request must carry an authorized transaction before it can run a workflow.

### Features

- Verifies signed HTTP workload requests and bound transactions.
- Checks workflow grants before dispatching inputs.
- Exchanges research authority for a read-only delegation and binds the file tool to the request.

### Non-Goals

The host supplies workload identities, issuer trust, proof signing, HTTPS termination, and service deployment.

---

## Getting Started

### Prerequisites

Use Python 3.10 through 3.14. Run the source installation commands from this package's directory.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_agent_wimse` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_agent_wimse` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_agent_wimse` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_agent_wimse
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/docs/readme/quick_start.py).

```python
from swarmauri_agent_wimse import WimseResearchAgent

assert WimseResearchAgent.__name__ == "WimseResearchAgent"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The quick start loads the package's public agent class without starting a service or calling a model.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/docs/readme/usage.py).

```python
from http.server import ThreadingHTTPServer
from swarmauri_agent_wimse import (
    FileToolEndpoint,
    TransactionPolicy,
    http_handler,
)


def file_server(files, workload_trust, transaction_keys):
    endpoint = FileToolEndpoint(
        tool=dict(files).__getitem__,
        audience="http://rich.ietf127.example:5063",
        trust=workload_trust,
        transaction=TransactionPolicy(
            issuer="http://rich.ietf127.example:5061",
            audience="rich.ietf127.example",
            keys=tuple(transaction_keys),
        ),
        research_subject="wimse://rich.ietf127.example/agent/research",
    )
    return ThreadingHTTPServer(("127.0.0.1", 5063), http_handler(endpoint))
```
<!-- readme-standards:end example.usage -->

Construct `ResearchAgentEndpoint` with a tool-capable model and mount it with `http_handler`. Each authorized request gets a fresh conversation and a toolkit with the bound `WimseFileTool`. Mount `WimseIngressEndpoint` at `/workflows/{workflow}/executions` and supply `(workload_subject, workflow_name)` grants.

### Configuration

Supply trusted issuer keys, expected workload subjects, the provisioned WIT and TbA signer, issuer and file service URLs, and each exact audience. The HTTP signature adapter uses the pinned TbA implementation.

### Error Handling

The endpoints reject invalid proofs, wrong audiences, replays, unauthorized workflow grants, and file paths outside the delegated transaction.

### Best Practices

Use distinct workload proof keys, keep file mappings under host control, and share the replay store across workers.

---

## Package Boundary

### What It Owns

Workflow admission, a research endpoint backed by a Swarmauri agent, and a request-bound file-reading tool.

### Public API and Import Surfaces

Import `WimseResearchAgent`, `WimseFileTool`, `WimseIngressEndpoint`, `ResearchAgentEndpoint`, `FileToolEndpoint`, `TransactionPolicy`, and `http_handler` from `swarmauri_agent_wimse`.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.agents` → `WimseResearchAgent` → `swarmauri_agent_wimse:WimseResearchAgent`
- `swarmauri.tools` → `WimseFileTool` → `swarmauri_agent_wimse:WimseFileTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

Inject the workflow handler, tool-capable model, workload trust, and transaction verification keys through the endpoint constructors.

### Protocol Consumers

A coordinator calls the research endpoint. The research workload uses its bound tool to call the file endpoint.

### Extensions

Register workflow functions that take a JSON `inputs` object and return a JSON-serializable result. Mount endpoints with `http_handler`.

---

## Operations and Readiness

### Operational Requirements

The example binds to loopback. A deployment supplies HTTPS and a shared replay store.

### Health and Observability

The host tracks request outcomes and workflow errors in its HTTP service.

### Security and Resource Limits

The file service verifies the WIT, HTTP proof, exact audience, replay state, and delegated file before reading.

### Compatibility

The manifest limits supported Python versions to 3.10 through 3.12.

---

## Verification

### Tests

Run `uv run --package swarmauri_agent_wimse pytest tests/unit/test_nine_hop_native.py` from the package directory. The suite exercises both nine-hop pairings with fresh keys and real TbA proofs, and needs no external runtime or live model credentials.

### Certification Status

The offline tests cover the scenarios listed above. No external certification is claimed.

### Evidence

The [native nine-hop tests](tests/unit/test_nine_hop_native.py) verify that unauthorized or invalid requests never trigger a workflow or an extra file read.

---

## FAQ

### Why

Delegate only the file read needed by a particular research request.

### How

Start with the source installation and import example, then use the constructor example under Usage.

### When

Choose this package when the host can provision and verify both workload credentials and bound transaction tokens.

---

## Documentation and Related Packages

### More Documentation

See [the native nine-hop integration](tests/unit/test_nine_hop_native.py) for the full request flow.

### Related Packages

The agent uses `swarmauri_standard` and the TbA WIMSE workload credential and HTTP proof profiles.

### Project Links

<!-- readme-standards:begin project-links -->
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_agent_wimse](https://pypi.org/project/swarmauri_agent_wimse/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [repository contribution guide](../../../AGENTS.md) and run the package tests when changing the public API.

### Development Setup

From `pkgs/`, run `uv run --directory standards/swarmauri_agent_wimse --package swarmauri_agent_wimse pytest`.

### Notes for Maintainers

Keep the plugin entry points, declared Python support, and maintained README examples aligned with package behavior.

---

## Governance

### Ownership and Decision Making

Swarmauri SDK maintainers review package changes in the repository.

### Standards and Policies

See the [repository README policy](../../../tools/readme/POLICY.md) for the package documentation contract.

### Lifecycle and Migration

This package is in planning. Review API and dependency changes before moving between source revisions.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_wimse/NOTICE) for attribution.
<!-- readme-standards:end notices -->
