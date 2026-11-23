# swarmauri_tts_elevenlabs_dialogue

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tts_elevenlabs_dialogue</strong></p>
<p align="center">Alpha Swarmauri Elevenlabs Dialogue text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/"><img alt="pypi: swarmauri_tts_elevenlabs_dialogue unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_tts_elevenlabs_dialogue%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml"><img alt="Source version: 0.1.0a1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0a1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/"><img alt="pypi downloads: swarmauri_tts_elevenlabs_dialogue: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_tts_elevenlabs_dialogue%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/README.md"><img alt="README hits: swarmauri_tts_elevenlabs_dialogue" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Alpha Swarmauri ElevenLabsDialogueTTS component. Ordered text/voice turns on the dialogue API, separate from single-speaker ElevenLabs TTS.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_elevenlabs_dialogue)](https://pepy.tech/projects/swarmauri_tts_elevenlabs_dialogue)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_elevenlabs_dialogue)](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_elevenlabs_dialogue)](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_elevenlabs_dialogue?label=swarmauri_tts_elevenlabs_dialogue&color=green)](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)

### Why This Package

`swarmauri_tts_elevenlabs_dialogue` isolates this responsibility: Alpha Swarmauri Elevenlabs Dialogue text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py) exposes `DialogueInput`, `DialogueTurn`, `ElevenLabsDialogueTTS`, `__version__`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tts_elevenlabs_dialogue` when your integration needs alpha Swarmauri Elevenlabs Dialogue text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Structured multi-voice files, async synthesis, streams and bounded batches.
- Provider-specific schemas and local input validation.
- Fixed provider endpoints and no automatic replay of billable requests.
- Python 3.10-3.14; no swarmauri_standard dependency.

### Non-Goals

`swarmauri_tts_elevenlabs_dialogue` owns alpha Swarmauri Elevenlabs Dialogue text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `httpx`, `pydantic`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add --prerelease allow swarmauri_tts_elevenlabs_dialogue
```

```bash
pip install --pre swarmauri_tts_elevenlabs_dialogue
```

This source candidate needs swarmauri_base>=0.11.0.dev12 published first.

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_tts_elevenlabs_dialogue` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_tts_elevenlabs_dialogue` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_tts_elevenlabs_dialogue` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_tts_elevenlabs_dialogue
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/docs/readme/quick_start.py).

```python
import os
from swarmauri_tts_elevenlabs_dialogue import (
    ElevenLabsDialogueTTS,
    DialogueTurn,
)

provider = ElevenLabsDialogueTTS(api_key=os.environ["ELEVENLABS_API_KEY"])
turns = (
    DialogueTurn(text="[curious] Hello?", voice_id=os.environ["VOICE_ONE"]),
    DialogueTurn(text="Hello back!", voice_id=os.environ["VOICE_TWO"]),
)
path = provider.predict(turns, "dialogue.mp3")
# await provider.apredict(turns, "dialogue.mp3")
# provider.batch({turns: "dialogue.mp3"})
# await provider.abatch({turns: "dialogue.mp3"}, max_concurrent=2)
# Iterate provider.stream(turns), or async-iterate provider.astream(turns).
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tts_elevenlabs_dialogue` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/docs/readme/usage.py).

```python
import os
from swarmauri_tts_elevenlabs_dialogue import (
    ElevenLabsDialogueTTS,
    DialogueTurn,
)

provider = ElevenLabsDialogueTTS(api_key=os.environ["ELEVENLABS_API_KEY"])
turns = (
    DialogueTurn(text="[curious] Hello?", voice_id=os.environ["VOICE_ONE"]),
    DialogueTurn(text="Hello back!", voice_id=os.environ["VOICE_TWO"]),
)
path = provider.predict(turns, "dialogue.mp3")
# await provider.apredict(turns, "dialogue.mp3")
# provider.batch({turns: "dialogue.mp3"})
# await provider.abatch({turns: "dialogue.mp3"}, max_concurrent=2)
# Iterate provider.stream(turns), or async-iterate provider.astream(turns).
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_tts_elevenlabs_dialogue` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tts_elevenlabs_dialogue` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tts_elevenlabs_dialogue` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DialogueInput`, `DialogueTurn`, `ElevenLabsDialogueTTS`, `__version__`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tts_elevenlabs_dialogue` is located in `standards` and owns alpha Swarmauri Elevenlabs Dialogue text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending. Source-declared APIs include `DialogueInput`, `DialogueTurn`, `ElevenLabsDialogueTTS`, `__version__`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tts_elevenlabs_dialogue`.

Source-declared exports or types: `DialogueInput`, `DialogueTurn`, `ElevenLabsDialogueTTS`, `__version__`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tts` → `ElevenLabsDialogueTTS` → `swarmauri_tts_elevenlabs_dialogue:ElevenLabsDialogueTTS`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tts_elevenlabs_dialogue` are `swarmauri-base`, `httpx`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tts_elevenlabs_dialogue` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tts_elevenlabs_dialogue`, use the source-declared public interfaces (`DialogueInput`, `DialogueTurn`, `ElevenLabsDialogueTTS`, `__version__`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tts_elevenlabs_dialogue` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tts_elevenlabs_dialogue`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py). The `swarmauri_tts_elevenlabs_dialogue` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tts_elevenlabs_dialogue` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tts_elevenlabs_dialogue` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_live_tts.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/tests/i9n/test_live_tts.py)
- [tests/unit/test_provider.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/tests/unit/test_provider.py)
- [tests/unit/test_stream.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/tests/unit/test_stream.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tts_elevenlabs_dialogue` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tts_elevenlabs_dialogue` provides alpha Swarmauri Elevenlabs Dialogue text-to-speech provider with file synthesis, async execution, streaming and bounded batches; live API verification pending; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tts_elevenlabs_dialogue`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tts_elevenlabs_dialogue` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/swarmauri_tts_elevenlabs_dialogue/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml) provide the supporting context for `swarmauri_tts_elevenlabs_dialogue`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.

### Project Links

<!-- readme-standards:begin project-links -->
- [Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_tts_elevenlabs_dialogue](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tts_elevenlabs_dialogue`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**API boundary**

Use a tuple of frozen DialogueTurn values, including as batch dictionary keys.
The order and voice IDs are preserved. Plain strings require default_voice_id;
that mode also works with TextToSpeechAgent. JSON text is never interpreted as a
turn list. The component enforces ten unique voices and a conservative 2000
character total, following the reliable-generation guidance. Model IDs are
eleven_v4 (default) and eleven_v3. output_format supports mp3_44100_128 (default),
pcm_24000 and ulaw_8000. Streaming uses /v1/text-to-dialogue/stream; output
retains the selected codec. Voice cloning, timestamps and WebSockets are outside
this interface. Raw PCM/mulaw need matching playback settings, not an MP3 decoder.

Primary reference: [provider API](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert).

**Verification and alpha status**

Live API behavior is **unverified**; tracked in [#6304](https://github.com/swarmauri/swarmauri-sdk/issues/6304). No paid synthesis was run. Retain version
0.1.0a1 and Development Status :: 3 - Alpha until maintainers review sufficient
live evidence. Mocked schemas do not prove playable audio, model availability,
voice controls, quality, latency or cost.

Live tests require SWARMAURI_LIVE_TTS=1 plus private ELEVENLABS_API_KEY. Configure SWARMAURI_TTS_VOICE and SWARMAURI_TTS_SECOND_VOICE
for your account. Select the model with SWARMAURI_TTS_MODEL. A key alone never
enables the suite. Default selection is predict only (one billable request).
SWARMAURI_LIVE_TTS_OPERATIONS selects a comma-separated operation list.
All six operations make eight billable requests per model. Never paste credentials or unmasked headers into issues or logs.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tts_elevenlabs_dialogue` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tts_elevenlabs_dialogue` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tts_elevenlabs_dialogue` source version is `0.1.0a1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tts_elevenlabs_dialogue/NOTICE) for attribution.
<!-- readme-standards:end notices -->
