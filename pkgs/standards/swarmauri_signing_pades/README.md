<p align="center">
    <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri PAdES Signer" width="320" />
</p>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_pades/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_pades?label=swarmauri_signing_pades&color=f97316" alt="PyPI Version" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_pades/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_pades" alt="Python Versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_pades/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_pades" alt="License" />
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pades/">
        <img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pades.svg" alt="Repo views" />
    </a>
</p>

---

# Swarmauri Signer PAdES

`PadesSigner` registers a PAdES (PDF Advanced Electronic Signatures) component
with the Swarmauri registry. It extends `SigningBase` and is designed to be
consumed by the shared `Signer` façade once the signing primitives are
implemented.

## Installation

### pip

```bash
pip install swarmauri_signing_pades
```

### uv

```bash
uv add swarmauri_signing_pades
```

To install directly:

```bash
uv pip install swarmauri_signing_pades
```

## Usage

```python
import asyncio
from swarmauri_signing_pades import PadesSigner


async def main() -> None:
    signer = PadesSigner()
    print("Features:", signer.supports()["features"])


if __name__ == "__main__":
    asyncio.run(main())
```

All coroutine implementations are placeholders that currently raise
`NotImplementedError`. They provide extension points for attached PDF signature
support.

## Contributing

Please read the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
if you would like to contribute improvements or documentation.
