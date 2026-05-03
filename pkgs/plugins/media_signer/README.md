![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/MediaSigner/">
        <img src="https://static.pepy.tech/badge/MediaSigner/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/media_signer/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/media_signer.svg"/></a>
    <a href="https://pypi.org/project/MediaSigner/">
        <img src="https://img.shields.io/pypi/pyversions/MediaSigner" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/MediaSigner/">
        <img src="https://img.shields.io/pypi/l/MediaSigner" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/MediaSigner/">
        <img src="https://img.shields.io/pypi/v/MediaSigner?label=MediaSigner&color=green" alt="PyPI - MediaSigner"/></a>
</p>
---

MediaSigner packages the asynchronous `Signer` facade that orchestrates registered
`SigningBase` providers. Moving the facade into a standalone plugin keeps the
core standards library lightweight while still enabling drop-in discovery of
specialised signers such as CMS, JWS, OpenPGP, PDF, and XMLDSig providers.

## Features

- **Unified signing faÃ§ade** â€“ talk to every installed `SigningBase` through a
  single async API that automatically discovers entry-point contributions.
- **Format-aware routing** â€“ delegates signing and verification to the provider
  registered for a format token such as `jws`, `pdf`, or `xmld`.
- **Optional plugin bundles** â€“ install curated extras (e.g. `[plugins]`) to
  bring in all available signer backends in one step.
- **Key-provider integration** â€“ share Swarmauri key providers with the facade
  so opaque key references resolve before signature creation.
- **Production-ready CLI** â€“ inspect capabilities, sign payloads, and verify
  results directly from the command line for fast automation.

## Installation

### Using `uv`

```bash
uv add MediaSigner

# install every optional backend
uv add "MediaSigner[plugins]"
```

The `[plugins]` extra pulls in CMS, JWS, OpenPGP, PDF, and XMLDSig signers.

### Using `pip`

```bash
pip install MediaSigner

# with every optional backend
pip install "MediaSigner[plugins]"
```

## Usage

```python
import asyncio

from MediaSigner import MediaSigner
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider

# Optionally pass a key provider so plugins receive a shared source for
# retrieving signing material.
key_provider: IKeyProvider | None = None
signer = MediaSigner(key_provider=key_provider)


async def sign_payload(payload: bytes) -> None:
    signatures = await signer.sign_bytes("jws", key="my-key", payload=payload)
    assert signatures, "At least one signature should be returned"
    print(signer.supports("jws"))


asyncio.run(sign_payload(b"payload"))
```

### Integrating a key provider

Any Swarmauri key provider can be shared with the facade so backends receive
ready-to-use key material:

```python
import asyncio

from MediaSigner import MediaSigner
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider

provider = InMemoryKeyProvider(keys={"local://demo": b"secret"})
signer = MediaSigner(key_provider=provider)


async def main() -> None:
    signatures = await signer.sign_bytes(
        "jws",
        key="local://demo",
        payload=b"demo",
        alg="HS256",
        opts={"kid": "demo"},
    )
    print(signatures[0].mode)


asyncio.run(main())
```

### Discover installed plugins

Use the facade to list installed signers and inspect their capabilities:

```python
for format_name in signer.supported_formats():
    capabilities = signer.supports(format_name)
    print(format_name, list(capabilities))
```

### Why this structure?

* **Separation of concerns** â€“ standards remain focused on common abstractions
  while the plugin encapsulates optional dependencies.
* **Explicit opt-in** â€“ downstream projects can install only the signing stacks
  they need via the curated extras.
* **Consistent ergonomics** â€“ usage matches the historical
  `swarmauri_standard.signing.Signer` import, preserving existing tutorials and
  code samples.

## Command line utility

MediaSigner ships a small CLI for quick inspection and automation:

```bash
media-signer list                 # List available formats
media-signer supports jws         # Show capability metadata
media-signer sign-bytes jws \
  --alg HS256 \
  --key key.json \
  --input payload.bin \
  --output signatures.json

media-signer verify-bytes jws \
  --input payload.bin \
  --sigs signatures.json \
  --opts verify-keys.json
```

The CLI expects JSON files describing `KeyRef` objects and verification
materials matching the selected plugin.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/media_signer>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/media_signer#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>
