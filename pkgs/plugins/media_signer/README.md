<p align="center">
  <img src="../../../assets/swarmauri.brand.theme.svg" alt="Swarmauri logotype" width="420" />
</p>

<h1 align="center">MediaSigner</h1>

<p align="center">
  <a href="https://img.shields.io/badge/status-experimental-ff6f61?style=for-the-badge"><img src="https://img.shields.io/badge/status-experimental-ff6f61?style=for-the-badge" alt="Status: experimental" /></a>
  <a href="https://img.shields.io/badge/license-Apache--2.0-0a6ebd?style=for-the-badge"><img src="https://img.shields.io/badge/license-Apache--2.0-0a6ebd?style=for-the-badge" alt="License: Apache-2.0" /></a>
  <a href="https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-4b8bbe?style=for-the-badge"><img src="https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-4b8bbe?style=for-the-badge" alt="Python versions" /></a>
</p>

MediaSigner packages the asynchronous `Signer` facade that orchestrates registered
`SigningBase` providers. Moving the facade into a standalone plugin keeps the
core standards library lightweight while still enabling drop-in discovery of
specialised signers such as CMS, JWS, OpenPGP, PDF, and XMLDSig providers.

## Installation

### Using `uv`

```bash
uv pip install MediaSigner
```

The `uv` installer resolves workspace dependencies automatically. Add the
`[plugins]` extra to bring in every optional signer at once:

```bash
uv pip install "MediaSigner[plugins]"
```

### Using `pip`

```bash
pip install MediaSigner
```

Extras mirror the `uv` workflow, so `pip install "MediaSigner[plugins]"`
installs the CMS, JWS, OpenPGP, PDF, and XMLDSig providers alongside the facade.

## Usage

```python
from MediaSigner import Signer
from swarmauri_core.keys.IKeyProvider import IKeyProvider

# Optionally pass a key provider so plugins receive a shared source for
# retrieving signing material.
key_provider: IKeyProvider | None = None
signer = Signer(key_provider=key_provider)

# The Signer facade inspects the registry to discover installed plugins. Once a
# plugin is available you can address it by its registered format token.
async def sign_payload(payload: bytes) -> None:
    signatures = await signer.sign_bytes("jws", key="my-key", payload=payload)
    assert signatures, "At least one signature should be returned"

# Capability queries surface exactly which operations each plugin supports.
print(signer.supports("jws"))
```

### Why this structure?

* **Separation of concerns** – standards remain focused on common abstractions
  while the plugin encapsulates optional dependencies.
* **Explicit opt-in** – downstream projects can install only the signing stacks
  they need via the curated extras.
* **Consistent ergonomics** – usage matches the historical
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
