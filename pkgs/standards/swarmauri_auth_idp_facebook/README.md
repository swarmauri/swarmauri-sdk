![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_facebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_facebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_facebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_facebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_facebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_facebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_facebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_facebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_facebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_facebook?label=swarmauri_auth_idp_facebook&color=green" alt="PyPI - swarmauri_auth_idp_facebook"/></a>
</p>

---

# Swarmauri Auth IDP Facebook

Facebook (Meta) OAuth 2.0, OAuth 2.1, and OIDC 1.0 login flows packaged for Swarmauri deployments.

## Features

- PKCE-enabled authorization URL generation with signed state payloads.
- Token exchange helpers that normalize identity data via Graph `/me` or verified ID tokens.
- Built-in retrying HTTP client tuned for Facebook authorization and Graph endpoints.
- ComponentBase-compatible models registering under `swarmauri.auth_idp` entry points.
- Support for both user-facing browser flows and confidential client OIDC integrations.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_facebook
```

### uv (project)

```bash
uv add swarmauri_auth_idp_facebook
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_facebook
```

## Usage

```python
from pydantic import SecretStr
from swarmauri_auth_idp_facebook import FacebookOAuth21Login

login = FacebookOAuth21Login(
    client_id="1234567890",
    client_secret=SecretStr("app-secret"),
    redirect_uri="https://app.example.com/auth/callback",
    state_secret=b"facebook-state-key",
)

print(login.client_id)
```

### Workflow Summary

1. Call `auth_url()` and redirect the browser to the returned Facebook login URL.
2. Persist the `state` token and validate it when handling the callback.
3. Exchange the authorization code via `exchange_and_identity()` to obtain tokens and profile data.
4. Persist the returned identity details to drive session and authorization workflows.

## Entry Points

- `swarmauri.auth_idp:FacebookOAuth20Login`
- `swarmauri.auth_idp:FacebookOAuth21Login`
- `swarmauri.auth_idp:FacebookOIDC10Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
