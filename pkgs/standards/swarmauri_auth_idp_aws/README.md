![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_aws/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_aws" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_aws/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_aws.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_aws/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_aws" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_aws/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_aws" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_aws/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_aws?label=swarmauri_auth_idp_aws&color=green" alt="PyPI - swarmauri_auth_idp_aws"/></a>
</p>

---

# Swarmauri Auth IDP AWS

AWS IAM Identity Center OAuth 2.0 / 2.1 logins packaged for Swarmauri deployments.

## Features

- PKCE-enabled authorization URL generation with signed state payloads.
- Token exchange helpers that return normalized payloads for downstream services.
- Optional identity resolver that hydrates user details via AWS Identity Store.
- ComponentBase-compatible models that register under `swarmauri.auth_idp` entry points.
- Retry-aware HTTP client tuned for AWS IAM Identity Center endpoints.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_aws
```

### uv (project)

```bash
uv add swarmauri_auth_idp_aws
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_aws
```

## Usage

```python
import asyncio
from swarmauri_auth_idp_aws import AwsOAuth21Login
from pydantic import SecretStr

login = AwsOAuth21Login(
    authorization_endpoint="https://example.awsapps.com/start/oauth2/authorize",
    token_endpoint="https://example.awsapps.com/start/oauth2/token",
    client_id="client-id",
    client_secret=SecretStr("client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=b"aws-workforce-state-key",
)

async def flow() -> None:
    auth = await login.auth_url()
    # Redirect the user to auth["url"], then capture the returned code/state.
    print(auth["url"])

asyncio.run(flow())
```

### Workflow Summary

1. Call `auth_url()` and redirect the browser to the returned URL.
2. Persist the `state` and compare it when handling the callback.
3. Exchange the authorization code via `exchange_and_identity()` to obtain tokens.
4. Optionally use `AwsIdentityResolver` to enrich identity details for the session.

## Entry Points

- `swarmauri.auth_idp:AwsOAuth20Login`
- `swarmauri.auth_idp:AwsOAuth21Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
