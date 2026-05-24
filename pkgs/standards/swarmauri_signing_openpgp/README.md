![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_signing_openpgp/">
        <img src="https://static.pepy.tech/badge/swarmauri_signing_openpgp/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_openpgp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_openpgp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_openpgp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_openpgp?label=swarmauri_signing_openpgp&color=green" alt="PyPI - swarmauri_signing_openpgp"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

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


