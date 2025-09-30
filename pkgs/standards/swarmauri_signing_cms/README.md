<p align="center">
    <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri Signing CMS" width="320" />
</p>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_cms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_cms?label=swarmauri_signing_cms&color=0d9488" alt="PyPI Version" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_cms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_cms" alt="Python Versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_cms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_cms" alt="License" />
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_cms/">
        <img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_cms.svg" alt="Repo views" />
    </a>
</p>

---

# Swarmauri Signing CMS

`CMSSigner` is a Swarmauri component stub that advertises CMS (PKCS#7) signing
capabilities through the unified registry. It inherits from
`swarmauri_base.signing.SigningBase`, uses the shared `register_type` decorator,
and accepts an optional key provider for dependency injection.

> **Note**
> This package currently ships scaffold code only. The signing and verification
> coroutines raise `NotImplementedError` until real CMS handling is wired in.

## Installation

### pip

```bash
pip install swarmauri_signing_cms
```

### uv

Add it to your managed project:

```bash
uv add swarmauri_signing_cms
```

Or install directly into the active environment:

```bash
uv pip install swarmauri_signing_cms
```

## Usage

```python
import asyncio
from swarmauri_signing_cms import CMSSigner


async def main() -> None:
    signer = CMSSigner()
    capabilities = signer.supports()
    print(capabilities["algs"])


if __name__ == "__main__":
    asyncio.run(main())
```

The class automatically registers itself under the `SigningBase` registry using
`type_name="cms"`. When the shared `Signer` façade from
`swarmauri_standards.signing` is constructed it discovers this plugin and can
route CMS signing requests to it.

## Contributing

Pull requests and issue reports are welcome! Please review the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
before submitting changes.
