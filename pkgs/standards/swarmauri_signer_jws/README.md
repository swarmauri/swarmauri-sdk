<p align="center">
    <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri JWS Signer" width="320" />
</p>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signer_jws/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signer_jws?label=swarmauri_signer_jws&color=0f766e" alt="PyPI Version" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signer_jws/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signer_jws" alt="Python Versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signer_jws/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signer_jws" alt="License" />
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signer_jws/">
        <img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signer_jws.svg" alt="Repo views" />
    </a>
</p>

---

# Swarmauri Signer JWS

`JWSSigner` is a registry-aware Swarmauri component that will eventually provide
JWS signing and verification using the Swarmauri `SigningBase` surface. The
current release is a scaffold that focuses on plugin registration and metadata.

## Installation

### pip

```bash
pip install swarmauri_signer_jws
```

### uv

```bash
uv add swarmauri_signer_jws
```

Or install into the active environment:

```bash
uv pip install swarmauri_signer_jws
```

## Usage

```python
import asyncio
from swarmauri_signer_jws import JWSSigner


async def main() -> None:
    signer = JWSSigner()
    print("Supported algorithms:", signer.supports()["algs"])


if __name__ == "__main__":
    asyncio.run(main())
```

The signer registers itself under the `SigningBase` registry as `"jws"`, so the
shared `Signer` façade from `swarmauri_standards.signing` can discover it.

## Status

The asynchronous signing and verification coroutines currently raise
`NotImplementedError`. They act as extension points for future JWS logic.

## Contributing

Have ideas for the implementation? Open an issue or submit a pull request after
reviewing the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
