![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_signing_openpgp/">
        <img src="https://static.pepy.tech/badge/swarmauri_signing_openpgp/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_openpgp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_openpgp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_openpgp" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_openpgp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_openpgp?label=swarmauri_signing_openpgp&color=green" alt="PyPI - swarmauri_signing_openpgp"/></a>
</p>
---

# Swarmauri Signing OpenPGP

`OpenPGPSigner` is the Swarmauri registry stub for OpenPGP signature workflows.
It inherits `SigningBase`, registers with `register_type`, and exposes the
metadata needed by the shared `Signer` faÃ§ade.

## Installation

### pip

```bash
pip install swarmauri_signing_openpgp
```

### uv

```bash
uv add swarmauri_signing_openpgp
```

Install into the current environment:

```bash
uv pip install swarmauri_signing_openpgp
```

## Usage

```python
import asyncio
from swarmauri_signing_openpgp import OpenPGPSigner


async def main() -> None:
    signer = OpenPGPSigner()
    print(signer.supports()["features"])


if __name__ == "__main__":
    asyncio.run(main())
```

All coroutine implementations currently raise `NotImplementedError`. They serve
as extension points for future OpenPGP envelope handling.

## Contributing

Contributions are welcome! See the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
for details.
