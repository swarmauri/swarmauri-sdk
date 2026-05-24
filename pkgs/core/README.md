![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_core/">
        <img src="https://static.pepy.tech/badge/swarmauri_core/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/l/swarmauri_core" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/v/swarmauri_core?label=swarmauri_core&color=green" alt="PyPI - swarmauri_core"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Core

`swarmauri_core` provides the interface contracts for the Swarmauri SDK. It is the package component authors use when they need stable abstract interfaces for agents, tools, LLMs, parsers, vector stores, cryptography, signing, key providers, transports, middleware, billing, storage, XMP, and other composable intelligence infrastructure components.

## Why Swarmauri Core?

`swarmauri_core` keeps component contracts separate from implementations. Package authors can depend on stable interfaces without pulling in every base class, provider adapter, model package, or runtime integration.

## FAQ

### Q: What belongs in `swarmauri_core`?

A: Interface contracts, protocol shapes, enums, and shared types for Swarmauri component families.

### Q: Should application developers instantiate classes from this package?

A: Usually no. Most application code uses concrete implementations from `swarmauri_standard`, community packages, or provider-specific packages. Component authors use `swarmauri_core` to implement the correct contract.

### Q: How does this package relate to `swarmauri_base`?

A: `swarmauri_core` defines interfaces. `swarmauri_base` implements reusable base classes and serialization behavior on top of those interfaces.

## What Is Included?

The package is intentionally implementation-light. It defines contracts, protocol shapes, enums, and shared types so implementation packages can interoperate without depending on each other directly.

Major interface families include:

- Agents and agent APIs: `IAgent`, conversation, parser, retrieval, toolkit, and vector-store agent mixins.
- LLM and multimodal prediction: text LLMs, tool LLMs, OCR, STT, TTS, and VLM interfaces.
- Documents and parsing: document contracts, parser contracts, chunkers, conversations, prompts, and prompt templates.
- Retrieval and vectors: vector, matrix, tensor, metric, similarity, vector-store comparator, deprecated distance compatibility contracts, vector store, and document store contracts.
- Security and trust: crypto, MRE crypto, cipher suites, signing, proof-of-possession, token services, key providers, certificates, and XMP embedding.
- Runtime infrastructure: middleware, transports, storage adapters, publishers, rate limits, tracing, state, service registries, and pipelines.
- Business systems: billing provider interfaces for customers, payments, invoices, subscriptions, refunds, payouts, risk, reporting, webhooks, and marketplace flows.

## Features

- Stable abstract interfaces for Swarmauri component packages.
- Shared types for crypto, signing, key management, transports, billing, and proof-of-possession workflows.
- Minimal runtime dependency footprint: `typing_extensions` and `aiofiles`.
- Interface-first design for packages that later inherit reusable behavior from `swarmauri_base`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_core
```

Install with `pip`:

```bash
pip install swarmauri_core
```

## Usage

Use `swarmauri_core` when defining a new implementation package or validating that a class satisfies a public Swarmauri contract.

```python
import asyncio
from typing import Any, Optional

from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.messages.IMessage import IMessage


class MinimalAgent(IAgent):
    def exec(
        self,
        input_data: Optional[Any] = None,
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return {"input": input_data, "kwargs": llm_kwargs or {}}

    async def aexec(
        self,
        input_str: Optional[str | IMessage] = "",
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return self.exec(input_str, llm_kwargs)

    def batch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return [self.exec(item, llm_kwargs) for item in inputs]

    async def abatch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return await asyncio.gather(
            *(self.aexec(item, llm_kwargs) for item in inputs)
        )
```

Implement a parser contract:

```python
from pathlib import Path

from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.parsers.IParser import IParser


class PlainTextParser(IParser):
    def parse(self, data: str | bytes | Path) -> list[IDocument]:
        raise NotImplementedError("Return concrete Document instances here.")
```

Implement a storage or retrieval contract in a concrete package, then expose the class through `swarmauri_base` and the public `swarmauri` namespace when appropriate.

## Component Author Workflow

1. Choose the closest interface from `swarmauri_core`.
2. Implement domain behavior in a package-specific class.
3. Add reusable serialization and registration behavior with `swarmauri_base` when the implementation should become a Swarmauri component.
4. Publish or register the implementation package through the appropriate `swarmauri.<kind>` entry point or namespace mapping.
5. Document installation and usage in the implementation package README.

## Related Packages

Foundational packages:

- [swarmauri](https://pypi.org/project/swarmauri/) provides the namespace importer and plugin discovery layer.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides reusable base classes built on these interfaces.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party implementations for common component kinds.

Packages built around specific core component kinds:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/) implements signing interfaces.
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/) composes crypto providers behind the crypto interface.
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/) implements key provider contracts.
- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/) implements transport contracts.
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/) implements storage adapter contracts.
- [swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/) implements middleware contracts.

## When To Use This Package

Use `swarmauri_core` when you are designing or implementing a Swarmauri-compatible component and need the interface contract. Use `swarmauri_base` when you also need reusable base-class behavior, serialization helpers, and component registration. Use `swarmauri_standard` when you want ready-to-use implementations.

## License

Apache-2.0

## Contributing

When adding or changing a core interface, keep the contract narrow, update downstream base classes where needed, add focused tests, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).


