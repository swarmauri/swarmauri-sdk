# swarmauri_agent_compacting

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_agent_compacting</strong></p>
<p align="center">Swarmauri text agent with manual and token-triggered conversation compaction.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_compacting/"><img alt="pypi: swarmauri_agent_compacting unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_agent_compacting%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/pyproject.toml"><img alt="Source version: 0.1.0.dev0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_compacting/"><img alt="pypi downloads: swarmauri_agent_compacting: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_agent_compacting%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/README.md"><img alt="README hits: swarmauri_agent_compacting" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_agent_compacting/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/tests/unit/test_CompactingAgent.py"><img alt="Tests: package tests" src="https://img.shields.io/static/v1?label=Tests&amp;message=package%20tests&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Run text conversations that keep recent turns and summarize older complete turns.

### Why This Package

Reduce the model input consumed by long conversations while preserving recent context.

### When to Use

Use this agent when a chat model needs to stay within a token budget across many turns.

### Features

- Manual compaction through `compact()` and `acompact()`.
- Token-triggered compaction before `exec()` and `aexec()` dispatch.
- Optional dedicated summarizer and an input limit enforced after compaction.

### Non-Goals

The caller supplies the model and a token counter for its input format.

---

## Getting Started

### Prerequisites

Use Python 3.10 through 3.14. Run the source installation commands from this package's directory.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_agent_compacting` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_agent_compacting` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_agent_compacting` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_agent_compacting
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/docs/readme/quick_start.py).

```python
from swarmauri_agent_compacting import CompactingAgent

assert CompactingAgent.__name__ == "CompactingAgent"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The quick start loads the package's public agent class without starting a service or calling a model.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/docs/readme/usage.py).

```python
from swarmauri_agent_compacting import CompactingAgent
from swarmauri_conversation_compacting import CompactingConversation


def make_agent(model, count_tokens):
    return CompactingAgent(
        llm=model,
        conversation=CompactingConversation(
            trigger_tokens=24_000,
            keep_recent_turns=4,
        ),
        count_input_tokens=count_tokens,
        max_input_tokens=28_000,
    )


def run_turn(agent, prompt):
    reply = agent.exec(prompt)
    changed = agent.compact()
    return reply, changed


async def run_turn_async(agent, prompt):
    reply = await agent.aexec(prompt)
    changed = await agent.acompact()
    return reply, changed
```
<!-- readme-standards:end example.usage -->

Construct an agent with the model and conversation, then run turns and compact as needed. Both compaction methods return `True` when they apply a shorter summary.

### Configuration

Set `trigger_tokens` on `CompactingConversation` for automatic compaction. Omit it for manual operation. Set `max_input_tokens` on the agent to enforce a limit.

### Error Handling

When the budget is still exceeded, the pending message remains in the conversation. Retry with `exec()` or `aexec()` without appending it again.

### Best Practices

Use one agent per conversation and submit turns sequentially. Provide the token counter again after restoring a serialized agent.

---

## Package Boundary

### What It Owns

Text-agent execution and orchestration of manual or automatic conversation compaction.

### Public API and Import Surfaces

Import `CompactingAgent` from `swarmauri_agent_compacting` and `CompactingConversation` from `swarmauri_conversation_compacting`.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.agents` → `CompactingAgent` → `swarmauri_agent_compacting:CompactingAgent`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

Pass a Swarmauri text model that appends its reply to the conversation and a callable that counts the model's input tokens.

### Protocol Consumers

Use `exec()` for synchronous text turns and `aexec()` in asynchronous callers. The batch interfaces process turns in order.

### Extensions

Configure a dedicated summarization model and its generation options when the chat model is unsuitable for summaries.

---

## Operations and Readiness

### Operational Requirements

Provide model credentials and a token counter appropriate for the deployed provider.

### Health and Observability

Observe compaction results and budget errors in the calling application.

### Security and Resource Limits

Set `max_input_tokens` to enforce a per-request input limit after the compaction attempt.

### Compatibility

The manifest limits supported Python versions to 3.10 through 3.12.

---

## Verification

### Tests

Run the package unit tests to exercise manual and threshold-triggered compaction in both synchronous and asynchronous execution.

### Certification Status

The offline tests cover the scenarios listed above. No external certification is claimed.

### Evidence

See the [package tests](tests/unit) for the compaction and budget behaviors.

---

## FAQ

### Why

Keep the source of token counts and summarization policy under application control.

### How

Start with the source installation and import example, then use the constructor example under Usage.

### When

Set a threshold for long-running conversations. Use manual compaction if the caller decides when to summarize.

---

## Documentation and Related Packages

### More Documentation

See [the CompactingAgent source](swarmauri_agent_compacting) for constructor parameters and execution methods.

### Related Packages

`swarmauri_conversation_compacting` owns the conversation and summary state.

### Project Links

<!-- readme-standards:begin project-links -->
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_agent_compacting](https://pypi.org/project/swarmauri_agent_compacting/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [repository contribution guide](../../../AGENTS.md) and run the package tests when changing the public API.

### Development Setup

From `pkgs/`, run `uv run --directory standards/swarmauri_agent_compacting --package swarmauri_agent_compacting pytest`.

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
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_compacting/NOTICE) for attribution.
<!-- readme-standards:end notices -->
