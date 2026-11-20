# swarmauri_tts_deepinfra

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tts_deepinfra</strong></p>
<p align="center">Alpha Swarmauri deepinfra text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tts_deepinfra/"><img alt="pypi: swarmauri_tts_deepinfra unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_tts_deepinfra%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml"><img alt="Source version: 0.1.0a2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0a2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tts_deepinfra/"><img alt="pypi downloads: swarmauri_tts_deepinfra: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_tts_deepinfra%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/README.md"><img alt="README hits: swarmauri_tts_deepinfra" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_tts_deepinfra/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Standalone alpha deepinfra speech synthesis for Swarmauri. DeepInfra `/v1/openai/audio/speech`: Kokoro, Chatterbox Turbo/Multilingual and Orpheus. Catalog model presence does not establish working coverage through this endpoint; verify each model. Native inference, voice cloning and voice design are excluded.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_deepinfra)](https://pepy.tech/projects/swarmauri_tts_deepinfra)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepinfra.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepinfra)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_deepinfra)](https://pypi.org/project/swarmauri_tts_deepinfra/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_deepinfra)](https://pypi.org/project/swarmauri_tts_deepinfra/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_deepinfra?label=swarmauri_tts_deepinfra&color=green)](https://pypi.org/project/swarmauri_tts_deepinfra/)

### Why This Package

`swarmauri_tts_deepinfra` isolates this responsibility: Alpha Swarmauri deepinfra text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py) exposes `DeepInfraTTS`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tts_deepinfra` when your integration needs alpha Swarmauri deepinfra text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- File generation through `predict` and `apredict`.
- Incremental audio through `stream` and `astream`, with connection cleanup.
- Synchronous batch execution and bounded async batches.
- Explicit provider URL, model, voice and output settings.
- No automatic retries of potentially billable generation requests.

Streaming yields binary HTTP audio chunks. Hosted buffering and time to first audio have not been measured.

### Non-Goals

`swarmauri_tts_deepinfra` owns alpha Swarmauri deepinfra text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `httpx`, `pydantic`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add --prerelease allow swarmauri_tts_deepinfra
```

```bash
pip install --pre swarmauri_tts_deepinfra
```

This source candidate requires the companion `swarmauri_base` release providing
`HttpTTSMixin` (`>=0.11.0.dev8`). Release that dependency before these wheels.

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_tts_deepinfra` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_tts_deepinfra` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_tts_deepinfra` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_tts_deepinfra
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/docs/readme/quick_start.py).

```python
import os
from swarmauri_tts_deepinfra import DeepInfraTTS

provider = DeepInfraTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    name="hexgrad/Kokoro-82M",
    voice="af_heart",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"First message": "first.mp3"})
# await provider.abatch({"Second message": "second.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tts_deepinfra` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/docs/readme/usage.py).

```python
import os
from swarmauri_tts_deepinfra import DeepInfraTTS

provider = DeepInfraTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    name="hexgrad/Kokoro-82M",
    voice="af_heart",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"First message": "first.mp3"})
# await provider.abatch({"Second message": "second.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```
<!-- readme-standards:end example.usage -->

Set `DEEPINFRA_API_KEY` in your environment, then:


Choose voices appropriate to the selected model. The filename does not change the
codec: select `response_format` explicitly and use a matching extension. The
component implements `TTSBase` and can be passed to `TextToSpeechAgent`.

### Configuration

Configure `swarmauri_tts_deepinfra` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tts_deepinfra` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py).

### Best Practices

Use the explicit `swarmauri_tts_deepinfra` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DeepInfraTTS`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tts_deepinfra` is located in `standards` and owns alpha Swarmauri deepinfra text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Source-declared APIs include `DeepInfraTTS`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tts_deepinfra`.

Source-declared exports or types: `DeepInfraTTS`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tts` → `DeepInfraTTS` → `swarmauri_tts_deepinfra:DeepInfraTTS`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tts_deepinfra` are `swarmauri-base`, `httpx`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tts_deepinfra` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tts_deepinfra`, use the source-declared public interfaces (`DeepInfraTTS`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tts_deepinfra` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tts_deepinfra`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py). The `swarmauri_tts_deepinfra` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tts_deepinfra` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tts_deepinfra` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_live_tts.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/tests/i9n/test_live_tts.py)
- [tests/unit/test_provider.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/tests/unit/test_provider.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tts_deepinfra` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tts_deepinfra` provides alpha Swarmauri deepinfra text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tts_deepinfra`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tts_deepinfra` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/swarmauri_tts_deepinfra/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml) provide the supporting context for `swarmauri_tts_deepinfra`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.

### Project Links

<!-- readme-standards:begin project-links -->
- [Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_tts_deepinfra](https://pypi.org/project/swarmauri_tts_deepinfra/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tts_deepinfra`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/standards/swarmauri_tts_deepinfra` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Verification and alpha status**

Live API behavior has **not** been verified by this change.
Tracked in [verification issue #6269](https://github.com/swarmauri/swarmauri-sdk/issues/6269). Offline tests validate
payloads, errors and transport behavior; they do not establish speech quality,
model availability or actual billed cost. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review live verification evidence.

Live tests are disabled even if a key is present. To explicitly authorize one
billable synthesis request, set `SWARMAURI_LIVE_TTS=1`, set `DEEPINFRA_API_KEY` privately,
and run this package's `tests/i9n` suite. Only `predict` runs by default. Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch` to
exercise all operations (eight requests including the two-item batches). Set
`SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` to select another model/voice.
Do not paste API keys into issues or logs.

Verification issue links and evidence requirements are maintained in
[the verification guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tts_deepinfra` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tts_deepinfra` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tts_deepinfra` source version is `0.1.0a2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).

The OpenAI-compatible route follows the provider's
[current Kokoro example](https://api.deepinfra.com/models/hexgrad/Kokoro-82M/docs/openai-tts-http.md).
Native schemas are separate packages: swarmauri_tts_deepinfra_kokoro,
swarmauri_tts_deepinfra_qwen3 and swarmauri_tts_deepinfra_qwen3_voicedesign.
They do not prove model coverage through this OpenAI-compatible adapter.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tts_deepinfra/NOTICE) for attribution.
<!-- readme-standards:end notices -->
