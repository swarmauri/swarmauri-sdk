<p align="center">
    <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri OpenPGP Signer" width="320" />
</p>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_openpgp?label=swarmauri_signing_openpgp&color=2563eb" alt="PyPI Version" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_openpgp" alt="Python Versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_openpgp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_openpgp" alt="License" />
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_openpgp/">
        <img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_openpgp.svg" alt="Repo views" />
    </a>
</p>

---

# Swarmauri Signer OpenPGP

`OpenPGPSigner` is the Swarmauri registry stub for OpenPGP signature workflows.
It inherits `SigningBase`, registers with `register_type`, and exposes the
metadata needed by the shared `Signer` façade.

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
