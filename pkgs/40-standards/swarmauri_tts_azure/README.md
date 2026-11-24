# swarmauri_tts_azure

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tts_azure</strong></p>
<p align="center">Alpha Swarmauri Azure Speech REST text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tts_azure/"><img alt="pypi: swarmauri_tts_azure" src="https://img.shields.io/pypi/v/swarmauri_tts_azure?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml"><img alt="Source version: 0.1.0a1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0a1&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tts_azure/"><img alt="Monthly PyPI downloads: swarmauri_tts_azure" src="https://img.shields.io/pypi/dm/swarmauri_tts_azure?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/README.md"><img alt="README hits: swarmauri_tts_azure" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tts_azure/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Alpha Swarmauri Azure Speech TTS provider. Public-cloud regional REST synthesis using a Speech resource key and escaped SSML. `name` is the voice ShortName, rather than a separate model ID.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_azure)](https://pepy.tech/projects/swarmauri_tts_azure)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_tts_azure.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_tts_azure)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_azure)](https://pypi.org/project/swarmauri_tts_azure/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_azure)](https://pypi.org/project/swarmauri_tts_azure/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_azure?label=swarmauri_tts_azure&color=green)](https://pypi.org/project/swarmauri_tts_azure/)

### Why This Package

`swarmauri_tts_azure` isolates this responsibility: Alpha Swarmauri Azure Speech REST text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py) exposes `AzureTTS`, `__version__`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tts_azure` when your integration needs alpha Swarmauri Azure Speech REST text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- File synthesis, asynchronous synthesis and bounded batches through TTSBase.
- Incremental HTTP audio with response cleanup on stream cancellation.
- Provider-specific authentication, encoding and region configuration.
- No automatic replay of billable synthesis requests.

### Non-Goals

`swarmauri_tts_azure` owns alpha Swarmauri Azure Speech REST text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `httpx`, `pydantic`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add --prerelease allow swarmauri_tts_azure
```

```bash
pip install --pre swarmauri_tts_azure
```

Python 3.10-3.14. This source candidate requires the companion
`swarmauri_base>=0.11.0.dev12` release before index installation.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tts_azure
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tts_azure
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tts_azure
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/docs/readme/quick_start.py).

```python
import os
from swarmauri_tts_azure import AzureTTS

provider = AzureTTS(
    api_key=os.environ["AZURE_SPEECH_KEY"],
    region=os.environ["AZURE_SPEECH_REGION"],
    name="en-US-JennyNeural",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tts_azure` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/docs/readme/usage.py).

```python
import os
from swarmauri_tts_azure import AzureTTS

provider = AzureTTS(
    api_key=os.environ["AZURE_SPEECH_KEY"],
    region=os.environ["AZURE_SPEECH_REGION"],
    name="en-US-JennyNeural",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```
<!-- readme-standards:end example.usage -->

Use the component with TextToSpeechAgent. Select a filename matching the output
format; HTTP chunks retain that codec. No realtime latency claim is made.

### Configuration

Configure `swarmauri_tts_azure` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tts_azure` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tts_azure` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AzureTTS`, `__version__`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tts_azure` is located in `standards` and owns alpha Swarmauri Azure Speech REST text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Source-declared APIs include `AzureTTS`, `__version__`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tts_azure`.

Source-declared exports or types: `AzureTTS`, `__version__`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tts` → `AzureTTS` → `swarmauri_tts_azure:AzureTTS`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tts_azure` are `swarmauri-base`, `httpx`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tts_azure` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tts_azure`, use the source-declared public interfaces (`AzureTTS`, `__version__`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tts_azure` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tts_azure`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py). The `swarmauri_tts_azure` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tts_azure` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tts_azure` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_live_tts.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/tests/i9n/test_live_tts.py)
- [tests/unit/test_provider.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/tests/unit/test_provider.py)
- [tests/unit/test_stream.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/tests/unit/test_stream.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tts_azure` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tts_azure` provides alpha Swarmauri Azure Speech REST text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tts_azure`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tts_azure` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/swarmauri_tts_azure/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml) provide the supporting context for `swarmauri_tts_azure`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.

### Project Links

<!-- readme-standards:begin project-links -->
- [Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_tts_azure](https://pypi.org/project/swarmauri_tts_azure/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tts_azure`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tts_azure` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Configuration and API scope**

The initial voices are en-US-JennyNeural (default), en-US-AriaNeural and
en-US-GuyNeural, with `locale="en-US"`. The input is plain text: markup and XML
characters are escaped into a single SSML voice element. Invalid XML control
characters fail locally. Custom voice deployments, raw user-supplied SSML,
Entra/STS token acquisition, sovereign/private endpoints and batch/Long Audio
APIs are excluded. Regional stock-voice availability needs live verification.

`output_format` supports audio-24khz-48kbitrate-mono-mp3 (default),
riff-24khz-16bit-mono-pcm (WAV), raw-24khz-16bit-mono-pcm,
raw-8khz-8bit-mono-mulaw and ogg-24khz-16bit-mono-opus.
Raw PCM/mulaw have no container header. Filenames do not change codecs.
The REST service limits generated audio to ten minutes; this adapter does not
silently split long text. Event-driven Speech SDK features need another interface.

Primary reference: [Azure Speech synthesis API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech).

**Verification and alpha status**

Live API behavior remains **unverified**; tracked in [#6302](https://github.com/swarmauri/swarmauri-sdk/issues/6302). No paid synthesis was run. Offline
contract tests do not establish account/model availability, output playability,
quality, latency or billed cost. Keep `Development Status :: 3 - Alpha` in
`pyproject.toml` until maintainers review sufficient live evidence.

The live suite requires explicit `SWARMAURI_LIVE_TTS=1` plus private AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.
A credential alone never enables it. Run the package's `tests/i9n` suite.
By default only predict runs (one billable request). Select additional operations
with `SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
(eight requests per model/voice because each batch has two inputs).
Set `SWARMAURI_TTS_MODEL` to the engine (Polly) or voice ShortName (Azure).
Azure does not use `SWARMAURI_TTS_VOICE`.
Never paste secrets or unmasked authorization headers in logs or issues.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tts_azure` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tts_azure` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tts_azure` source version is `0.1.0a1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_azure/NOTICE) for attribution.
<!-- readme-standards:end notices -->
