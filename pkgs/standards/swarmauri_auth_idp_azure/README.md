![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_azure/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_azure" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_azure/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_azure.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_azure/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_azure" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_azure/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_azure" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_azure/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_azure?label=swarmauri_auth_idp_azure&color=green" alt="PyPI - swarmauri_auth_idp_azure"/></a>
</p>

---

# Swarmauri Auth IDP Azure AD

Azure Active Directory / Entra ID OAuth 2.0, OAuth 2.1, and OIDC 1.0 login flows packaged for Swarmauri deployments.

## Features

- PKCE-enabled authorization URL generation with signed state payloads to protect verifiers.
- Token exchange helpers that return normalized identity details from Microsoft Graph.
- Built-in retrying HTTP client for resilient calls against Azure AD and Graph endpoints.
- ComponentBase-compatible models that register under `swarmauri.auth_idp` entry points.
- Support for both interactive browser logins and confidential client OIDC workflows.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_azure
```

### uv (project)

```bash
uv add swarmauri_auth_idp_azure
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_azure
```

## Usage

```python
from pydantic import SecretStr
from swarmauri_auth_idp_azure import AzureOAuth21Login

login = AzureOAuth21Login(
    tenant="organizations",
    client_id="00000000-0000-0000-0000-000000000000",
    client_secret=SecretStr("client-secret"),
    redirect_uri="https://app.example.com/auth/callback",
    state_secret=b"azure-ad-state-key",
)

print(login.client_id)
```

### Workflow Summary

1. Call `auth_url()` and redirect the browser to the returned Microsoft login URL.
2. Persist the `state` token and compare it when handling the callback.
3. Exchange the authorization code via `exchange_and_identity()` to obtain tokens and Graph profile data.
4. Persist the returned tokens or computed identity details for session and authorization workflows.

## Entry Points

- `swarmauri.auth_idp:AzureOAuth20Login`
- `swarmauri.auth_idp:AzureOAuth21Login`
- `swarmauri.auth_idp:AzureOIDC10Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
