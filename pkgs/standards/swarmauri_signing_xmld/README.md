![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_signing_xmld/">
        <img src="https://static.pepy.tech/badge/swarmauri_signing_xmld/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_xmld/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_xmld.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_xmld/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_xmld/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_xmld" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_xmld/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_xmld?label=swarmauri_signing_xmld&color=green" alt="PyPI - swarmauri_signing_xmld"/></a>
</p>
---

# Installation

### uv

```bash
uv pip install swarmauri_signing_xmld
```

### pip

```bash
pip install swarmauri_signing_xmld
```

## Usage

```python
from swarmauri_signing_xmld import XMLDSigner

signer = XMLDSigner()
xml_payload = """<note><to>Alice</to><from>Bob</from></note>""".encode()

signature = await signer.sign_bytes(
    key={
        "kind": "pem",
        "private_key": "/path/to/private_key.pem",
        "certificate": "/path/to/certificate.pem",
    },
    payload=xml_payload,
)
```
