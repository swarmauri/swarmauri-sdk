# swarmauri_base

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_base</strong></p>
<p align="center">Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_base/"><img alt="pypi: swarmauri_base" src="https://img.shields.io/pypi/v/swarmauri_base"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml"><img alt="Source version: 0.11.0.dev13" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev13&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml"><img alt="Layer: base" src="https://img.shields.io/static/v1?label=Layer&amp;message=base&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_base/"><img alt="Monthly PyPI downloads: swarmauri_base" src="https://img.shields.io/pypi/dm/swarmauri_base"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md"><img alt="README hits: swarmauri_base" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/20-bases/swarmauri_base/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_base`: Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.

### Why This Package

`swarmauri_base` turns Swarmauri interfaces into reusable component foundations. It gives implementation packages consistent Pydantic modeling, resource metadata, dynamic subtype registration, serialization, and family-specific base behavior.

### When to Use

Use `swarmauri_base` when implementing a Swarmauri component that needs serialization, registration, and shared base behavior. Use `swarmauri_core` when you only need interface definitions. Use implementation packages such as `swarmauri_standard` or individual component packages when you need ready-to-run behavior.

### Features

- `ComponentBase` for Pydantic-backed Swarmauri components with `type`, `resource`, `name`, and `version` fields.
- `DynamicBase` and `SubclassUnion` for discriminated-union deserialization from concrete `type` values.
- JSON, YAML, and TOML serialization through Pydantic plus Swarmauri mixins.
- Base classes for agents, chains, chunkers, conversations, documents, embeddings, LLMs, tools, toolkits, vector stores, parsers, prompts, transports, middleware, signing, crypto, key providers, tokens, billing, XMP, and more.
- Default mixins for logging, service metadata, batch behavior, retrieval behavior, storage behavior, and component-family-specific workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_base` owns reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml) declares runtime dependencies including `pyyaml`, `httpx`, `numpy`, `pydantic`, `starlette`, `swarmauri-core`, `swarmauri-typing`, `toml`, `tomli`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_base
```

Install with `pip`:

```bash
pip install swarmauri_base
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_base
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_base
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_base
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/docs/readme/quick_start.py).

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_model()
class StoreConfig(ComponentBase):
    type: Literal["StoreConfig"] = "StoreConfig"
    name: str
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_base` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/docs/readme/usage.py).

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_model()
class StoreConfig(ComponentBase):
    type: Literal["StoreConfig"] = "StoreConfig"
    name: str
```
<!-- readme-standards:end example.usage -->

Create a typed component by inheriting from `ComponentBase`:


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

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py) references configuration keys `PATH`, `PEAGEN_CONFIG`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_base` source raises `CapabilityError`, `DuplicateToolCallError`, `EvaluationError`, `FileNotFoundError`, `IndexError`, `KeyError`, `NotImplementedError`, `PoPBindingError`, `PoPParseError`, `PoPVerificationError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_base` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `FullUnion`, `SubclassUnion`, `register_model`, `register_type`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_base` is located in `base` and owns reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure. Source-declared APIs include `FullUnion`, `SubclassUnion`, `register_model`, `register_type`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_base`.

Source-declared exports or types: `FullUnion`, `SubclassUnion`, `register_model`, `register_type`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_base` are `pyyaml`, `httpx`, `numpy`, `pydantic`, `starlette`, `swarmauri-core`, `swarmauri-typing`, `toml`, `tomli`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri-demo-package-maintenance`, `swarmauri_billing_adyen`, `swarmauri_billing_authorize_net`, `swarmauri_billing_braintree`, `swarmauri_billing_paypal`, `swarmauri_billing_paystack`, `swarmauri_billing_razorpay`, `swarmauri_billing_square`, `swarmauri_certs_acme`, `swarmauri_certs_azure`, `swarmauri_certs_cfssl`, `swarmauri_certs_crlverifyservice`, `swarmauri_certs_csronly`, `swarmauri_certs_ocspverify`, `swarmauri_certservice_aws_kms`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_base`, use the source-declared public interfaces (`FullUnion`, `SubclassUnion`, `register_model`, `register_type`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_base` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_base`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py). The `swarmauri_base` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_base` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_base` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/integration/test_middleware_starlette.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/tests/integration/test_middleware_starlette.py)
- [tests/unit/test_chain_context_base.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/tests/unit/test_chain_context_base.py)
- [tests/unit/test_dynamic_schema_examples.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/tests/unit/test_dynamic_schema_examples.py)
- [tests/unit/test_embedxmp_base.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/tests/unit/test_embedxmp_base.py)
- [tests/unit/test_git_filter_base.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/tests/unit/test_git_filter_base.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_base` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What is ComponentBase?**

A: `ComponentBase` is the common Pydantic-backed base for Swarmauri components. It carries fields such as `type`, `resource`, `name`, and `version`, and participates in dynamic component registration.

**Q: What is SubclassUnion used for?**

A: `SubclassUnion` lets Pydantic models hydrate registered concrete component types from serialized payloads that include a `type` discriminator.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_base`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py) for the exact types and signatures involved.

### When

**Q: When should I use swarmauri_base instead of swarmauri_core?**

A: Use `swarmauri_base` when building a real component implementation. Use `swarmauri_core` when you only need the abstract interface contract.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/swarmauri_base/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml) provide the supporting context for `swarmauri_base`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

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

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_base](https://pypi.org/project/swarmauri_base/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When adding or changing a base class, keep it aligned with the corresponding `swarmauri_core` interface, preserve direct plugin instantiation patterns, update exports and tests, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

### Development Setup

Work from the `pkgs/20-bases/swarmauri_base` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Composable execution bases**

Matching `executions`, `tasks`, `workflows`, `permissions`, `delegation` and
`invocations` modules provide abstract component bases for interchangeable
implementations. They do not add a transport or authenticator family.
See the [composition guide](../../../docs/examples/composable-execution/README.md).

`swarmauri_base` provides the reusable base classes, mixins, and dynamic component model used by Swarmauri SDK implementations. It builds on `swarmauri_core` interfaces and adds Pydantic models, typed component registration, JSON/YAML/TOML serialization, logging helpers, service helpers, and base classes for each major component family.

**Component Families**

`swarmauri_base` includes base classes and mixins for these component kinds:

- AI and agent workflow: agents, chains, conversations, prompts, prompt templates, pipelines, swarms, task management strategies, tool LLMs, tools, toolkits, LLMs, VLMs, OCR, STT, and TTS.
- Data and retrieval: documents, document stores, embeddings, vectors, vector stores, parsers, schema converters, data connectors, state, service registries, and storage adapters.
- Math and evaluation: vector-store comparators, deprecated distance compatibility shims, inner products, matrices, measurements, metrics, norms, pseudometrics, seminorms, similarities, tensors, evaluators, evaluator pools, and evaluator results.
- Runtime and infrastructure: transports, middleware, publishers, rate limits, logging handlers, logging formatters, loggers, tracing-oriented mixins, services, and programs.
- Security and trust: cert services, crypto, MRE crypto, cipher suites, signing, proof-of-possession helpers, key providers, token services, XMP embedding, and git filters.
- Business integrations: billing provider base classes and mixins for customers, hosted checkout, payments, invoices, subscriptions, refunds, payouts, reports, promotions, risk, marketplace, and webhooks.

**Component Author Workflow**

1. Start with the relevant interface in [swarmauri_core](https://pypi.org/project/swarmauri_core/).
2. Inherit the matching base class from `swarmauri_base`.
3. Add a stable `type` literal and `resource` value.
4. Register the model or subtype with `ComponentBase.register_model()` or `ComponentBase.register_type(...)`.
5. Add package entry points or namespace mappings through [swarmauri](https://pypi.org/project/swarmauri/) when the implementation should be discoverable.
6. Document installation, direct instantiation, serialization behavior, and any provider-specific configuration in the implementation package README.

**Run storage**

`swarmauri_base.run_stores.RunStoreBase` implements shared checkpoint revision
rules. A backend supplies an insert, a read, and an atomic compare-and-swap.

**HTTP TTS transport**

`tts.HttpTTSMixin` shares file, streaming and bounded async batch transport for
standalone TTS providers. Provider packages own request schemas, fixed URLs and
stream decoding. `_speech_endpoint(streaming)` selects provider-owned unary
and streaming routes; `_audio_content(response)` decodes unary JSON audio when
needed. `_speech_request(payload, streaming)` prepares headers and body once for
providers that require XML or an exact body signature. Existing JSON/binary
providers retain their default behavior. Transport does
not replay potentially billable requests.

`tts.JsonAudioTTSMixin` decodes complete base64/data-URI audio from JSON for
file and batch workflows. It rejects URL audio and malformed/empty data, and
checks WAV headers when WAV is requested. Providers validate their own status
and format fields. Its stream/astream methods raise locally; a complete JSON
response is never labeled an incremental stream.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_base` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_base` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_base` source version is `0.11.0.dev13`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/NOTICE) for attribution.
<!-- readme-standards:end notices -->
