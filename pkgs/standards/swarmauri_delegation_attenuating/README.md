![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_delegation_attenuating

[![Downloads](https://static.pepy.tech/badge/swarmauri_delegation_attenuating/month)](https://pepy.tech/project/swarmauri_delegation_attenuating)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_delegation_attenuating.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_delegation_attenuating)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_delegation_attenuating)
[![License](https://img.shields.io/pypi/l/swarmauri_delegation_attenuating)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_delegation_attenuating)](https://pypi.org/project/swarmauri_delegation_attenuating)

Interchangeable delegations component for the composable execution framework.

## Features

- Export `AttenuatingDelegationService` with SDK interface/base-class inheritance and entry-point discovery.
- Keep user authority, workload identity, lifecycle and delivery dependencies explicit.
- Reuse existing service registries, transports, checkpoints and token providers.
- Support Python 3.10, 3.11 and 3.12.

## Installation

These packages introduce unreleased core/base APIs. Install the matching workspace revision together; do not combine with older published core/base releases. Release validation must publish compatible dependency versions first.

```sh
uv pip install ./pkgs/standards/swarmauri_delegation_attenuating
pip install ./pkgs/standards/swarmauri_delegation_attenuating
```

## Usage

The following is composition code. Injected dependency names are host configuration, not bundled mock providers. Async statements run inside an async function.

```python
from swarmauri_delegation_attenuating import AttenuatingDelegationService

service = AttenuatingDelegationService(
    grants=grant_store, tasks=task_store, policy=permission_policy,
    tokens=token_service, kid=signing_key_id, issuer=issuer,
    edges=frozenset({("agent:A", "agent:B")}),
)
# Trusted broker operations: authenticate callers before passing identities.
root = service.root(task_id, "agent:A", permissions, remaining_depth=1)
child = service.delegate(root.grant_id, "agent:A", "agent:B", permissions)
credential = await service.credential(
    child.grant_id, "agent:A", "agent:B", permissions[0]
)
service.revoke(root.grant_id)
# Later admission rejects the child even if its JWT has not expired.
```

See [the complete architecture and deployment guide](../../../docs/examples/composable-execution/README.md) for concrete local commands, live OIDC integration, HTTP hosting, lifecycle semantics and failure recovery.

## Verification

From `pkgs/`, with the workspace dependencies installed:

```sh
uv run --package swarmauri_delegation_attenuating --directory standards/swarmauri_delegation_attenuating pytest
uv run --package swarmauri_delegation_attenuating --directory standards/swarmauri_delegation_attenuating ruff check .
```

Tests use real signing and stores where applicable; scripted models are explicitly identified fixtures. No live provider interoperability is claimed by offline tests.

## Contributing

Follow the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/AGENTS.md).
