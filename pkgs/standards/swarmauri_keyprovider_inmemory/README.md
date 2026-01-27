![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_inmemory/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_inmemory" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_inmemory/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_inmemory.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_inmemory/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_inmemory" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_inmemory/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_inmemory" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_inmemory/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_inmemory?label=swarmauri_keyprovider_inmemory&color=green" alt="PyPI - swarmauri_keyprovider_inmemory"/></a>
</p>

---

# Swarmauri In‑Memory Key Provider

Volatile, in‑memory key provider for Swarmauri. All key material is kept strictly in process memory (no disk writes). Ideal for testing, CI, and ephemeral gateways where persistence is not desired. Not intended for long‑term or production storage of secrets.

## Installation

Install the package with your preferred Python tooling:

```bash
pip install swarmauri_keyprovider_inmemory
```

```bash
poetry add swarmauri_keyprovider_inmemory
```

```bash
pip install uv
uv pip install swarmauri_keyprovider_inmemory
```

## Usage

Create and manage symmetric (or opaque/asymmetric placeholder) keys entirely in memory. The snippet below creates a new symmetric key and returns a `KeyRef` with material present when allowed by the export policy.

```python
import asyncio
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyClass,
    KeyAlg,      # optional, not enforced by the provider
    KeyUse,
    ExportPolicy,
)


async def main() -> None:
    provider = InMemoryKeyProvider()

    # Create a symmetric key kept only in memory
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,             # optional hint – not strictly enforced
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,  # material may be present
        label="session-key",
    )
    ref = await provider.create_key(spec)
    assert ref.kid and ref.version == 1
    # ref.material may be populated depending on export_policy

    # Rotate to get a new version, still in memory only
    ref2 = await provider.rotate_key(ref.kid)
    assert ref2.version == 2

    # List available versions
    versions = await provider.list_versions(ref.kid)
    print(versions)  # e.g., (1, 2)

    # Import existing key material
    imported = await provider.import_key(
        spec,
        material=b"\x00" * 32,
    )
    assert imported.version == 1

    # Fetch current version
    current = await provider.get_key(ref.kid)
    assert current.version == max(versions)

    # Destroy a specific version or the whole key
    await provider.destroy_key(ref.kid, version=1)   # delete only v1
    await provider.destroy_key(imported.kid)         # delete all versions

    # Utilities
    rand = await provider.random_bytes(16)
    okm = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
    print(len(rand), len(okm))


asyncio.run(main())
```

## Capabilities

- Class support: `symmetric`, `asymmetric (opaque)`
- Features: `create`, `import`, `rotate`, `destroy`, `list_versions`, `get_key`, `random_bytes`, `hkdf`
- No persistence: data is lost when the process exits
- Not supported: JWK/JWKS export (will raise `NotImplementedError`)

## Security Considerations

- Keys exist only for the lifetime of the Python process; restarting drops all material.
- No hardware isolation or disk persistence is provided.
- Use only for development, CI, or other ephemeral scenarios.

## Notes

- Exported `KeyRef.material` presence depends on the `ExportPolicy`. Use `ExportPolicy.NONE` to prevent material from being surfaced to callers.
- For gateways, set this provider as the default to keep keys off disk in development and CI.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.