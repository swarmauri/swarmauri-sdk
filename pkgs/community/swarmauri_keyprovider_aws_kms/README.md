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
