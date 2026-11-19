![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_invoker_default

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_invoker_default)](https://pepy.tech/project/swarmauri_invoker_default)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_invoker_default.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_invoker_default)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_invoker_default)](https://pypi.org/project/swarmauri_invoker_default)
[![License](https://img.shields.io/pypi/l/swarmauri_invoker_default)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_invoker_default?label=swarmauri_invoker_default&color=green)](https://pypi.org/project/swarmauri_invoker_default)

Interchangeable invocations component for the composable execution framework.

## Features

- Export `DefaultInvoker` with SDK interface/base-class inheritance and entry-point discovery.
- Keep user authority, workload identity, lifecycle and delivery dependencies explicit.
- Reuse existing service registries, transports, checkpoints and token providers.
- Support Python 3.10, 3.11, 3.12, 3.13 and 3.14.

## Installation

Install the package with its declared dependencies. The composable APIs require swarmauri_core 0.11.0.dev8 or newer and swarmauri_base 0.11.0.dev13 or newer within the declared version bounds.

```sh
uv pip install ./pkgs/standards/swarmauri_invoker_default
pip install ./pkgs/standards/swarmauri_invoker_default
```

## Usage

The following is composition code. Injected dependency names are host configuration, not bundled mock providers. Async statements run inside an async function.

```python
from swarmauri_transport_httpx import HttpxClient
from swarmauri_invoker_default import DefaultInvoker

invoker = DefaultInvoker(
    services=service_registry, policy=permission_policy,
    edges=edge_bindings, authorities=authority_strategies,
    http_client=HttpxClient(), local_endpoints=receiving_apps,
)
result = await invoker.invoke(request, trusted_invocation_context)
# Model arguments do not supply actor identities, grants, or JWTs.
```

See [the complete architecture and deployment guide](../../../docs/examples/composable-execution/README.md) for concrete local commands, live OIDC integration, HTTP hosting, lifecycle semantics and failure recovery.

## Verification

From `pkgs/`, with the workspace dependencies installed:

```sh
uv run --package swarmauri_invoker_default --directory standards/swarmauri_invoker_default pytest
uv run --package swarmauri_invoker_default --directory standards/swarmauri_invoker_default ruff check .
```

Tests use real signing and stores where applicable; scripted models are explicitly identified fixtures. No live provider interoperability is claimed by offline tests.

## Contributing

Follow the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/AGENTS.md).
