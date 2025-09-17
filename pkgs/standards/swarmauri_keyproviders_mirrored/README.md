![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyproviders_mirrored" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyproviders_mirrored/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyproviders_mirrored.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyproviders_mirrored" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyproviders_mirrored" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyproviders_mirrored?label=swarmauri_keyproviders_mirrored&color=green" alt="PyPI - swarmauri_keyproviders_mirrored"/></a>
</p>

---

# Swarmauri Mirrored Key Provider

An asynchronous failover key provider that keeps a primary provider as the
system of record while best-effort mirroring material to a secondary provider
for redundancy.

## Features

- Write operations (`create`, `import`, `rotate`, `destroy`) execute on the
  primary provider first and then mirror to the secondary provider when
  possible.
- `mirror_mode` governs what is replicated: `public_only` (default) mirrors only
  public material, `full` attempts to replicate private material when export
  policy allows, and `none` disables replication while retaining read
  failover.
- Read operations (`get_key`, `get_public_jwk`, `jwks`, `list_versions`,
  `random_bytes`, `hkdf`) favor the primary provider and fail over to the
  secondary provider when `fail_open_reads` is enabled.
- JWKS responses merge keys from both providers, preferring primary entries when
  the same `kid` appears in both sets.
- Maintains an in-memory mapping of mirrored key identifiers to coordinate
  destroy operations and failover reads—persist or rebuild this mapping if you
  need cross-process continuity.
- Optional extras add canonical JSON (`jsoncanon`) and CBOR (`cbor`) support for
  consumers that require deterministic encodings.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_keyproviders_mirrored
```

```bash
poetry add swarmauri_keyproviders_mirrored
```

```bash
uv pip install swarmauri_keyproviders_mirrored
```

Enable extras for canonicalization when needed:

```bash
pip install swarmauri_keyproviders_mirrored[jsoncanon]
```

```bash
pip install swarmauri_keyproviders_mirrored[cbor]
```

## Usage

The provider mirrors newly created keys to the secondary provider and fails open
on reads when the primary becomes unavailable.

```python
import asyncio

from swarmauri_keyproviders_mirrored import MirroredKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


async def main() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(
        primary,
        secondary,
        mirror_mode="public_only",
        fail_open_reads=True,
    )

    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    created = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(created.kid, created.version)

    await primary.destroy_key(created.kid, created.version)
    mirrored = await provider.get_public_jwk(created.kid, created.version)

    assert mirrored["x"] == jwk["x"]
    print(f"Failover retrieved Ed25519 key from secondary provider: {mirrored['kid']}")


if __name__ == "__main__":
    asyncio.run(main())
```

In the example above the primary key is destroyed after mirroring, forcing
`MirroredKeyProvider` to serve the public key from the secondary provider.
Although mirrored keys may have different `kid` values, the public material
remains identical and ready for verification.

## Mirror Modes

- `public_only` *(default)* — Mirrors public key material and JWKS entries when
  available.
- `full` — Attempts to mirror private material when export policy permits,
  falling back to public-only replication otherwise.
- `none` — Disables replication while still permitting read failover to the
  secondary provider.

## Failover Semantics

The `fail_open_reads` flag controls whether read operations fall back to the
secondary provider when the primary raises an exception. Disable it to surface
primary errors immediately.

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as
`MirroredKeyProvider`.
