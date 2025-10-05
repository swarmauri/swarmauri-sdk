<p align="center">
    <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri Signing PDF" width="320" />
</p>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_pdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_pdf?label=swarmauri_signing_pdf&color=f97316" alt="PyPI Version" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_pdf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_pdf" alt="Python Versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_pdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_pdf" alt="License" />
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pdf/">
        <img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pdf.svg" alt="Repo views" />
    </a>
</p>

---

# Swarmauri Signing PDF

`PDFSigner` builds on the CMS signer to produce detached signatures suitable for
embedding in PDF documents. It exposes the standard Swarmauri `SigningBase`
interface and cooperates with the shared `Signer` façade.

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
