![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_hierarchical/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_hierarchical" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_hierarchical/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_hierarchical.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_hierarchical/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_hierarchical" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_hierarchical/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_hierarchical" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_hierarchical/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_hierarchical?label=swarmauri_keyprovider_hierarchical&color=green" alt="PyPI - swarmauri_keyprovider_hierarchical"/></a>
</p>

---

# Swarmauri Hierarchical Key Provider

Plugin providing a policy-driven composite key provider capable of routing
key operations across multiple child providers. It implements the
`IKeyProvider` interface and exposes a single `HierarchicalKeyProvider`
class.

## Overview

`HierarchicalKeyProvider` composes a mapping of named child providers and
routes every key operation to the correct child according to declarative
policies.  It offers:

- **Create/import routing** – specify ordered [`CreateRule`](#routing-policy)
  objects that match key class, algorithm, usage, or export policy. The first
  rule that matches a `KeySpec` wins.
- **Automatic discovery** – when looking up an unknown key identifier (KID)
  the provider probes each child until it finds the owning provider and caches
  the association for future calls.
- **Persistent indexing** – optionally persist the learned KID → provider map
  to JSON via the `index_file` argument so the routing cache survives process
  restarts.
- **Capability passthrough** – rotate, destroy, list, JWKS, HKDF, and random
  byte requests are forwarded transparently to the owning (or designated)
  child provider. JWKS responses are merged across children while avoiding
  duplicate KIDs.
- **Heuristic fallback** – if no policy matches a create/import request the
  provider falls back to sensible defaults: asymmetric keys prefer children
  named like KMS/PKCS#11, symmetric keys prefer local/file providers, and
  otherwise the first registered child is used.

## Installation

Choose the installer that matches your workflow.

### pip

```bash
pip install swarmauri_keyprovider_hierarchical
```

### Poetry

```bash
poetry add swarmauri_keyprovider_hierarchical
```

### uv

```bash
uv venv  # create (or reuse) a virtual environment
source .venv/bin/activate
uv pip install swarmauri_keyprovider_hierarchical
```

If you are already inside a uv-managed environment you can shorten the last
two steps to `uv pip install swarmauri_keyprovider_hierarchical`.

## Quickstart

The example below wires two `LocalKeyProvider` instances behind a
`HierarchicalKeyProvider`. Symmetric keys are routed to a local provider while
asymmetric keys land on a provider named `kms`. The composite provider also
serves random bytes and JWKS responses for all children.

<!-- example-start -->
```python
"""Create keys across multiple providers with policy-driven routing."""

import asyncio

from swarmauri_keyprovider_hierarchical import HierarchicalKeyProvider, CreateRule
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)


async def main() -> None:
    children = {
        "kms": LocalKeyProvider(),
        "local": LocalKeyProvider(),
    }
    provider = HierarchicalKeyProvider(
        children,
        create_policy=[
            CreateRule(provider="kms", klass=KeyClass.asymmetric),
            CreateRule(provider="local", klass=KeyClass.symmetric),
        ],
        randomness_provider="local",  # designate a child for random_bytes
    )

    symmetric_spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    asymmetric_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )

    symmetric_ref = await provider.create_key(symmetric_spec)
    asymmetric_ref = await provider.create_key(asymmetric_spec)
    random_token = await provider.random_bytes(16)
    jwks = await provider.jwks()

    print(f"Symmetric key kid: {symmetric_ref.kid}")
    print(f"Asymmetric key kid: {asymmetric_ref.kid}")
    print(f"Random token length: {len(random_token)} bytes")
    print(f"JWKS entries: {len(jwks['keys'])}")


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- example-end -->

Running the script prints the generated key identifiers, confirms the random
token length, and shows how many public keys were merged into the JWKS
document.

## Routing policy

`CreateRule` is a dataclass that narrows matching by any combination of
attributes:

- `provider` (required): the name of the child provider to route to.
- `klass`: limit matches to a specific `KeyClass` (symmetric or asymmetric).
- `algs`: iterable of allowed `KeyAlg` values.
- `uses`: iterable of desired `KeyUse` values; at least one requested use must
  intersect with the spec.
- `export_policies`: iterable of `ExportPolicy` values.

Rules are evaluated in order, and the first match wins. When an import policy
is not supplied, create rules are re-used for imports.

## Index persistence & discovery

Pass `index_file` to persist the in-memory KID → provider cache as JSON. On
startup, any known mappings are re-loaded (invalid provider names are skipped).
When a lookup is made for an unknown KID the provider probes each child with a
`get_key` call; if a child recognizes the KID the mapping is remembered and
future calls avoid probing. Destroying a key (without specifying a version)
removes the cached entry.

## Randomness & key derivation

Use the `randomness_provider` and `derivation_provider` keyword arguments to
pin those helper methods to a specific child. If they are omitted the first
registered provider is used for both random bytes and HKDF requests.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.