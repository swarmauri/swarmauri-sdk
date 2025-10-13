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

`CMSSigner` delivers production-ready
[Cryptographic Message Syntax (CMS)](https://www.rfc-editor.org/rfc/rfc5652)
and [S/MIME](https://www.rfc-editor.org/rfc/rfc8551) signing utilities for the
Swarmauri platform. The signer integrates with the common
`SigningBase` registry and works seamlessly with Swarmauri certificate
providers so that applications can create, distribute, and verify PKCS#7
signatures end-to-end.

## Features

- Detached and attached PKCS#7 signatures with DER or PEM serialization
- S/MIME friendly defaults for email payloads
- Streaming, digest, and structured-envelope signing helpers
- Signature verification with certificate chain enforcement
- First-class interoperability with Swarmauri key providers and certificate
  authorities

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

The snippets below illustrate how to bootstrap certificates, create CMS and
S/MIME signatures, and verify results with Swarmauri components.

### Bootstrapping CMS credentials

Use `swarmauri_certs_x509` together with a key provider to issue a
CMS-capable signing certificate with the correct [email protection
Extended Key Usage](https://www.rfc-editor.org/rfc/rfc5280#section-4.2.1.12).

```python
import asyncio
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider


async def build_smime_identity():
    key_provider = LocalKeyProvider()
    certs = X509CertService()

    ca_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="Example CMS CA",
    )
    ca_key = await key_provider.create_key(ca_spec)
    ca_cert = await certs.create_self_signed(
        ca_key,
        {"CN": "Example CMS Root", "O": "Example Org"},
        extensions={
            "basic_constraints": {"ca": True, "path_len": 0},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
                "key_cert_sign": True,
                "crl_sign": True,
            },
        },
    )

    leaf_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="CMS Signer",
    )
    leaf_key = await key_provider.create_key(leaf_spec)
    csr = await certs.create_csr(
        leaf_key,
        {"CN": "cms-signer.example", "emailAddress": "signer@example.org"},
        san={"email": ["signer@example.org"]},
    )
    leaf_cert = await certs.sign_cert(
        csr,
        ca_key,
        ca_cert=ca_cert,
        extensions={
            "basic_constraints": {"ca": False},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
            },
            "extended_key_usage": {"oids": ["emailProtection"]},
        },
    )

    cms_key_ref = {
        "kind": "pem",
        "private_key": leaf_key.material,
        "certificate": leaf_cert,
        "extra_certificates": [ca_cert],
    }
    trust_chain = [ca_cert]
    return cms_key_ref, trust_chain


cms_key_ref, trust_chain = asyncio.run(build_smime_identity())
```

`cms_key_ref` can now be supplied to the `CMSSigner` for both CMS and S/MIME
operations. The returned `trust_chain` is useful when verifying signatures.

### Detached CMS signing & verification

```python
import asyncio
from swarmauri_signing_cms import CMSSigner


async def sign_and_verify(message: bytes):
    signer = CMSSigner()
    signatures = await signer.sign_bytes(
        cms_key_ref,
        message,
        alg="SHA256",
        opts={"encoding": "der"},
    )

    ok = await signer.verify_bytes(
        message,
        signatures,
        opts={"trusted_certs": trust_chain},
    )
    return signatures[0].artifact, ok


artifact, verified = asyncio.run(sign_and_verify(b"important document"))
print(f"Signature length: {len(artifact)} bytes, verified={verified}")
```

`sign_bytes` produces a detached PKCS#7 signature suitable for archival or
transport alongside the original payload. Verification succeeds when at least
one signature chains back to a trusted certificate.

### S/MIME attached signing

Attached S/MIME signatures encapsulate the message body and are typically
distributed using the `application/pkcs7-mime` content type.

```python
import asyncio
from email.message import EmailMessage
from email import policy
from swarmauri_signing_cms import CMSSigner


async def create_smime(message: EmailMessage):
    payload = message.as_bytes(policy=policy.SMTP)
    signer = CMSSigner()
    signature = await signer.sign_bytes(
        cms_key_ref,
        payload,
        opts={"attached": True, "encoding": "pem"},
    )
    verified = await signer.verify_bytes(
        payload,
        signature,
        opts={"trusted_certs": trust_chain},
    )
    return signature[0].artifact, verified


msg = EmailMessage()
msg["From"] = "signer@example.org"
msg["To"] = "recipient@example.net"
msg["Subject"] = "Quarterly Statement"
msg.set_content("Please review the attached statement.")

smime_bytes, ok = asyncio.run(create_smime(msg))
if ok:
    with open("statement.p7m", "wb") as fp:
        fp.write(smime_bytes)
```

The resulting `statement.p7m` file contains a fully formed S/MIME envelope that
can be delivered via email or downloaded from an API.

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
