![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_signing_pdf/">
        <img src="https://static.pepy.tech/badge/swarmauri_signing_pdf/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_pdf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_pdf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_pdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_pdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_pdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_pdf?label=swarmauri_signing_pdf&color=green" alt="PyPI - swarmauri_signing_pdf"/></a>
</p>
---

# Swarmauri Signing PDF

`PDFSigner` builds on the CMS signer to produce detached signatures suitable for
embedding in PDF documents. It exposes the standard Swarmauri `SigningBase`
interface and cooperates with the shared `Signer` faÃ§ade.

## Installation

### pip

```bash
pip install swarmauri_signing_pdf
```

### uv

```bash
uv add swarmauri_signing_pdf
```

To install directly:

```bash
uv pip install swarmauri_signing_pdf
```

## Usage

```python
import asyncio
from swarmauri_signing_pdf import PDFSigner


async def main() -> None:
    signer = PDFSigner()
    print("Features:", signer.supports()["features"])


if __name__ == "__main__":
    asyncio.run(main())
```

The signer delegates cryptographic work to the CMS implementation, returning
standardised `Signature` payloads ready to embed into PDF workflows.

## Contributing

Please read the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
if you would like to contribute improvements or documentation.
