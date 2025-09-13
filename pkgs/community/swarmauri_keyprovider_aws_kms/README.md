![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_aws_kms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_aws_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_aws_kms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_aws_kms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_aws_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_aws_kms?label=swarmauri_keyprovider_aws_kms&color=green" alt="PyPI - swarmauri_keyprovider_aws_kms"/></a>

</p>

---

# Swarmauri AWS KMS Key Provider

Community plugin providing an AWS KMS backed `KeyProvider` for Swarmauri.

## Features
- Manage RSA and AES keys via AWS KMS
- Publish JWKs following [RFC 7517](https://datatracker.ietf.org/doc/html/rfc7517)
- Generate cryptographically secure random bytes

## Installation
```bash
pip install swarmauri_keyprovider_aws_kms
```

## Usage
```python
from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider

provider = AwsKmsKeyProvider(region="us-east-1")
```
