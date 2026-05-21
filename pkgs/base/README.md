![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_base/">
        <img src="https://static.pepy.tech/badge/swarmauri_base/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/base/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/base.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_base/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_base/">
        <img src="https://img.shields.io/pypi/l/swarmauri_base" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_base/">
        <img src="https://img.shields.io/pypi/v/swarmauri_base?label=swarmauri_base&color=green" alt="PyPI - swarmauri_base"/></a>
</p>

# Swarmauri Base

`swarmauri_base` provides the reusable base classes, mixins, and dynamic component model used by Swarmauri SDK implementations. It builds on `swarmauri_core` interfaces and adds Pydantic models, typed component registration, JSON/YAML/TOML serialization, logging helpers, service helpers, and base classes for each major component family.

## Why Swarmauri Base?

`swarmauri_base` turns Swarmauri interfaces into reusable component foundations. It gives implementation packages consistent Pydantic modeling, resource metadata, dynamic subtype registration, serialization, and family-specific base behavior.

## FAQ

### Q: What is `ComponentBase`?

A: `ComponentBase` is the common Pydantic-backed base for Swarmauri components. It carries fields such as `type`, `resource`, `name`, and `version`, and participates in dynamic component registration.

### Q: What is `SubclassUnion` used for?

A: `SubclassUnion` lets Pydantic models hydrate registered concrete component types from serialized payloads that include a `type` discriminator.

### Q: When should I use `swarmauri_base` instead of `swarmauri_core`?

A: Use `swarmauri_base` when building a real component implementation. Use `swarmauri_core` when you only need the abstract interface contract.

## Features

- `ComponentBase` for Pydantic-backed Swarmauri components with `type`, `resource`, `name`, and `version` fields.
- `DynamicBase` and `SubclassUnion` for discriminated-union deserialization from concrete `type` values.
- JSON, YAML, and TOML serialization through Pydantic plus Swarmauri mixins.
- Base classes for agents, chains, chunkers, conversations, documents, embeddings, LLMs, tools, toolkits, vector stores, parsers, prompts, transports, middleware, signing, crypto, key providers, tokens, billing, XMP, and more.
- Default mixins for logging, service metadata, batch behavior, retrieval behavior, storage behavior, and component-family-specific workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_base
```

Install with `pip`:

```bash
pip install swarmauri_base
```

## Usage

Create a typed component by inheriting from `ComponentBase`:

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_model()
class StoreConfig(ComponentBase):
    type: Literal["StoreConfig"] = "StoreConfig"
    name: str
```

Register and hydrate concrete subtypes with `SubclassUnion`:

```python
from typing import Literal

from pydantic import BaseModel
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion


@ComponentBase.register_model()
class StoreConfig(ComponentBase):
    type: Literal["StoreConfig"] = "StoreConfig"
    name: str


@ComponentBase.register_type(StoreConfig, "SqliteStoreConfig")
class SqliteStoreConfig(StoreConfig):
    type: Literal["SqliteStoreConfig"] = "SqliteStoreConfig"
    path: str


class StoreEnvelope(BaseModel):
    store: SubclassUnion[StoreConfig]


envelope = StoreEnvelope.model_validate_json(
    '{"store":{"type":"SqliteStoreConfig","name":"local","path":"./data.db"}}'
)

assert isinstance(envelope.store, SqliteStoreConfig)
```

Build a concrete tool from `ToolBase`:

```python
from typing import Any, Literal

from swarmauri_base.tools.ToolBase import ToolBase


class EchoTool(ToolBase):
    type: Literal["EchoTool"] = "EchoTool"
    name: str = "echo"
    description: str = "Return the input payload."

    def __call__(self, payload: Any) -> Any:
        return payload


tool = EchoTool()
assert tool("hello") == "hello"
assert tool.batch(["a", "b"]) == ["a", "b"]
```

## Component Families

`swarmauri_base` includes base classes and mixins for these component kinds:

- AI and agent workflow: agents, chains, conversations, prompts, prompt templates, pipelines, swarms, task management strategies, tool LLMs, tools, toolkits, LLMs, VLMs, OCR, STT, and TTS.
- Data and retrieval: documents, document stores, embeddings, vectors, vector stores, parsers, schema converters, data connectors, state, service registries, and storage adapters.
- Math and evaluation: distances, inner products, matrices, measurements, metrics, norms, pseudometrics, seminorms, similarities, tensors, evaluators, evaluator pools, and evaluator results.
- Runtime and infrastructure: transports, middleware, publishers, rate limits, logging handlers, logging formatters, loggers, tracing-oriented mixins, services, and programs.
- Security and trust: cert services, crypto, MRE crypto, cipher suites, signing, proof-of-possession helpers, key providers, token services, XMP embedding, and git filters.
- Business integrations: billing provider base classes and mixins for customers, hosted checkout, payments, invoices, subscriptions, refunds, payouts, reports, promotions, risk, marketplace, and webhooks.

## Component Author Workflow

1. Start with the relevant interface in [swarmauri_core](https://pypi.org/project/swarmauri_core/).
2. Inherit the matching base class from `swarmauri_base`.
3. Add a stable `type` literal and `resource` value.
4. Register the model or subtype with `ComponentBase.register_model()` or `ComponentBase.register_type(...)`.
5. Add package entry points or namespace mappings through [swarmauri](https://pypi.org/project/swarmauri/) when the implementation should be discoverable.
6. Document installation, direct instantiation, serialization behavior, and any provider-specific configuration in the implementation package README.

## Related Packages

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides the interface contracts that these base classes implement.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party components built from these base classes.
- [swarmauri_typing](https://pypi.org/project/swarmauri_typing/) provides typing utilities used by dynamic union machinery.

Packages built on component-kind bases:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/) builds on signing base behavior.
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/) builds on crypto base behavior.
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/) builds on key provider base behavior.
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/) builds on storage adapter base behavior.
- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/) builds on transport base behavior.
- [swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/) builds on middleware base behavior.

## When To Use This Package

Use `swarmauri_base` when implementing a Swarmauri component that needs serialization, registration, and shared base behavior. Use `swarmauri_core` when you only need interface definitions. Use implementation packages such as `swarmauri_standard` or individual component packages when you need ready-to-run behavior.

## License

Apache-2.0

## Contributing

When adding or changing a base class, keep it aligned with the corresponding `swarmauri_core` interface, preserve direct plugin instantiation patterns, update exports and tests, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
