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

## Example workflows

The package ships ready-to-run demonstrations inside
`swarmauri_signing_cms/examples/cms_and_smime_examples.py`. They generate
ephemeral key material using the `cryptography` library so you can explore CMS
and S/MIME flows without external tooling.

### Prepare signing material

```python
from swarmauri_signing_cms.examples.cms_and_smime_examples import build_ephemeral_identity

key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
```

`key_ref` is the structure expected by `CMSSigner`. It contains the PEM encoded
private key, end-entity certificate, and (optionally) a chain. The helper also
returns a PEM trust anchor that can be supplied during verification.

### Create a detached CMS signature

```python
import asyncio
from swarmauri_signing_cms import CMSSigner
from swarmauri_signing_cms.examples.cms_and_smime_examples import (
    build_ephemeral_identity,
    cms_detached_signature,
)


async def main() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    signer = CMSSigner()
    signature = await cms_detached_signature(signer, key_ref, [trust_anchor])
    print("Signature mode:", signature.mode)
    print("Hash algorithm:", signature.alg)


if __name__ == "__main__":
    asyncio.run(main())
```

The helper signs raw bytes, verifies the result using the provided trust store,
and returns the resulting `Signature` instance. Detached artifacts are encoded
as DER by default, but you can pass `opts={"attached": False, "encoding": "pem"}`
when you need PEM output for downstream systems.

### Assemble an S/MIME message

```python
import asyncio
from email import policy
from email.generator import BytesGenerator
from io import BytesIO

from swarmauri_signing_cms import CMSSigner
from swarmauri_signing_cms.examples.cms_and_smime_examples import (
    build_ephemeral_identity,
    smime_attached_message,
)


async def main() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    envelope = await smime_attached_message(CMSSigner(), key_ref, [trust_anchor])
    buffer = BytesIO()
    BytesGenerator(buffer, policy=policy.SMTP).flatten(envelope)
    print(buffer.getvalue().decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```

`smime_attached_message` requests an attached CMS signature in PEM form
(`smime.p7s`) and wraps the payload inside a `multipart/signed` envelope. The
helper verifies the artifact against the provided trust anchor before returning
the message container.

### Inspect the CMS certificate chain

```python
import asyncio
from swarmauri_signing_cms import CMSSigner
from swarmauri_signing_cms.examples.cms_and_smime_examples import (
    build_ephemeral_identity,
    cms_detached_signature,
    describe_certificate_chain,
)


async def describe() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    signature = await cms_detached_signature(CMSSigner(), key_ref, [trust_anchor])
    for subject in describe_certificate_chain(signature):
        print(subject)


asyncio.run(describe())
```

`Signature.cert_chain_der` contains DER-encoded certificates returned by the
signing routine. `describe_certificate_chain` converts those blobs back into
`cryptography.x509.Certificate` instances so you can display or persist the
chain.

## Contributing

Pull requests and issue reports are welcome! Please review the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
before submitting changes.
