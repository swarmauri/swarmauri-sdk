# swarmauri_middleware_llamaguard

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_llamaguard</strong></p>
<p align="center">Middleware for inspecting and filtering unsafe content using LlamaGuard</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_llamaguard/"><img alt="pypi: swarmauri_middleware_llamaguard" src="https://img.shields.io/pypi/v/swarmauri_middleware_llamaguard"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_llamaguard/"><img alt="Monthly PyPI downloads: swarmauri_middleware_llamaguard" src="https://img.shields.io/pypi/dm/swarmauri_middleware_llamaguard"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/README.md"><img alt="README hits: swarmauri_middleware_llamaguard" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_middleware_llamaguard/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A Starlette middleware that wraps Groq's ``llama-guard-3-8b`` model to provide end-to-end content inspection for both inbound requests and outbound responses. The middleware is designed to slot into any Starlette application and enforce safety policies before your handlers are invoked.

### Why This Package

`swarmauri_middleware_llamaguard` isolates this responsibility: Middleware for inspecting and filtering unsafe content using LlamaGuard. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py) exposes `LlamaGuardMiddleware`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_middleware_llamaguard` when your integration needs middleware for inspecting and filtering unsafe content using LlamaGuard. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Real-time scanning of incoming request bodies and outgoing responses (including streaming responses).
- Configurable language model injection ? provide your own :class:`~swarmauri_standard.llms.GroqModel` or let the middleware create one for you.
- Graceful degradation when no model is configured (traffic is allowed but logged).

### Non-Goals

`swarmauri_middleware_llamaguard` owns middleware for inspecting and filtering unsafe content using LlamaGuard. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `starlette`, `python-dotenv`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the workflow that matches your project tooling:

- **pip**

  ```bash
  pip install swarmauri_middleware_llamaguard
  ```

- **poetry**

  ```bash
  poetry add swarmauri_middleware_llamaguard
  ```

- **uv**

  ```bash
  uv add swarmauri_middleware_llamaguard
  ```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_llamaguard
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_llamaguard
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_llamaguard
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

1. Configure your Groq API key (either export ``GROQ_API_KEY`` or pass ``api_key`` when constructing the middleware).
2. Attach the middleware to your Starlette application:


The middleware will block requests or responses when ``llama-guard-3-8b`` labels the payload as ``unsafe``.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/docs/readme/quick_start.py).

```python
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

app = Starlette()
middleware = LlamaGuardMiddleware()  # Uses GROQ_API_KEY from the environment


async def llama_guard(request: Request, call_next):
    return await middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=llama_guard)


async def health_check(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/health", health_check)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_llamaguard` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/docs/readme/usage.py).

```python
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

app = Starlette()
middleware = LlamaGuardMiddleware()  # Uses GROQ_API_KEY from the environment


async def llama_guard(request: Request, call_next):
    return await middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=llama_guard)


async def health_check(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/health", health_check)
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_middleware_llamaguard` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_llamaguard` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py).

### Best Practices

Use the explicit `swarmauri_middleware_llamaguard` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `LlamaGuardMiddleware`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_llamaguard` is located in `standards` and owns middleware for inspecting and filtering unsafe content using LlamaGuard. Source-declared APIs include `LlamaGuardMiddleware`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_llamaguard`.

Source-declared exports or types: `LlamaGuardMiddleware`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `LlamaGuardMiddleware` → `swarmauri_middleware_llamaguard:LlamaGuardMiddleware`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_llamaguard` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `starlette`, `python-dotenv`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_llamaguard` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_llamaguard`, use the source-declared public interfaces (`LlamaGuardMiddleware`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_llamaguard` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_llamaguard`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py). The `swarmauri_middleware_llamaguard` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_llamaguard` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_llamaguard` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_examples.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/tests/test_readme_examples.py)
- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_LlamaGuardMiddleware.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/tests/unit/test_LlamaGuardMiddleware.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_llamaguard` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_middleware_llamaguard` provides middleware for inspecting and filtering unsafe content using LlamaGuard; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_llamaguard`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_llamaguard` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/swarmauri_middleware_llamaguard/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml) provide the supporting context for `swarmauri_middleware_llamaguard`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_llamaguard](https://pypi.org/project/swarmauri_middleware_llamaguard/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_middleware_llamaguard` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Middleware behavior**

``LlamaGuardMiddleware`` inspects content by default with Groq's ``llama-guard-3-8b`` model. Provide an API key via the ``api_key`` argument or the ``GROQ_API_KEY`` environment variable to enable enforcement. When no model is available the middleware logs a warning and treats all content as safe so that applications can continue to function while you configure credentials.

Both JSON responses and streaming responses are inspected. Unsafe content results in an HTTP 400 response with a descriptive error payload.

**Example: Local safety checks without Groq**

The middleware also accepts a custom language model implementation. The following self-contained example demonstrates how to supply a stub model for local development or tests while still benefiting from end-to-end request inspection.

```python
# README Example: Basic request filtering
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_llamaguard import LlamaGuardMiddleware
from swarmauri_standard.messages.AgentMessage import AgentMessage


class StubGuardModel:
    def predict(self, conversation, *args, **kwargs):
        latest = str(conversation.get_last().content).lower()
        verdict = "unsafe" if "malicious" in latest else "safe"
        conversation.add_message(AgentMessage(content=verdict))


app = Starlette()
middleware = LlamaGuardMiddleware(llm=StubGuardModel())


async def llama_guard(request: Request, call_next):
    return await middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=llama_guard)

async def echo(request: Request):
    return JSONResponse(await request.json())


app.add_route("/echo", echo, methods=["POST"])

with TestClient(app) as client:
    assert client.post("/echo", json={"message": "hello"}).status_code == 200
    assert (
        client.post("/echo", json={"message": "malicious content"}).status_code
        == 400
    )
```

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_llamaguard` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_llamaguard` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_llamaguard` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_llamaguard/NOTICE) for attribution.
<!-- readme-standards:end notices -->
