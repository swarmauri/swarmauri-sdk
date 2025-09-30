![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/signer-name-tbd/">
        <img src="https://img.shields.io/pypi/v/signer-name-tbd?label=SignerNameTBD&color=blue" alt="PyPI - Version"/></a>
    <a href="https://pypi.org/project/signer-name-tbd/">
        <img src="https://img.shields.io/pypi/pyversions/signer-name-tbd" alt="PyPI - Python Version"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/SignerNameTBD">
        <img src="https://img.shields.io/github/license/swarmauri/swarmauri-sdk" alt="License"/></a>
</p>

---

# SignerNameTBD Plugin

`SignerNameTBD` packages the Swarmauri signing facade so it can be consumed like any other plugin. The facade dynamically discovers `SigningBase` implementations that register themselves with the Swarmauri component registry and provides a high-level API for the most common signing and verification workflows.

## Installation

### Using `uv`

```bash
uv add signer-name-tbd
```

The `uv add` command installs the facade along with the Swarmauri base and core packages that provide the shared component registry and cryptographic type definitions.

### Using `pip`

```bash
pip install signer-name-tbd
```

This performs the same installation using the default Python package index. Ensure that your active environment already contains the Swarmauri workspace packages or that they are installed as dependencies alongside the facade.

## Usage

```python
from SignerNameTBD import Signer
from swarmauri_core.crypto.types import KeyRef

signer = Signer()
supported = signer.supported_formats()
print("Available formats:", supported)

# Example signing flow (async context required)
# signatures = await signer.sign_bytes("Ed25519Key" as KeyRef, b"payload", fmt="jws")
```

1. Import the facade directly from the plugin package.
2. Instantiate `Signer` optionally passing an `IKeyProvider` so that downstream plugins have access to shared key material.
3. Call capability helpers such as `supported_formats()` or `supports(fmt)` to inspect what each registered plugin advertises.
4. Execute signing or verification calls by selecting a registered format identifier (e.g., `"jws"`, `"cms"`). Each call defers to the underlying plugin and forwards options, canonicalization hints, and policy requirements unchanged.

Because the facade loads plugins lazily from the global registry, additional signer packages can be installed without modifying the facade itself. Simply install the desired signer (for example `swarmauri_signer_jws`) and rerun your program; the plugin will self-register when imported and the facade will automatically expose its capabilities.
