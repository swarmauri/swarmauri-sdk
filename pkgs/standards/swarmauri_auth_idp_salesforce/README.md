![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_salesforce/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_salesforce" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_salesforce/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_salesforce.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_salesforce/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_salesforce" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_salesforce/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_salesforce" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_salesforce/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_salesforce?label=swarmauri_auth_idp_salesforce&color=green" alt="PyPI - swarmauri_auth_idp_salesforce"/></a>
</p>

---

# Swarmauri Auth IDP Salesforce

Salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers packaged for Swarmauri deployments.

## Features

- PKCE-enabled Authorization Code flows that integrate with Salesforce authorization servers.
- JWT bearer app clients for Salesforce OAuth 2.0, OAuth 2.1, and OIDC 1.0 machine identities.
- Discovery-driven OAuth 2.1/OIDC login that verifies ID tokens against Salesforce JWKS.
- UserInfo and Identity URL fallbacks for normalized profile payloads.
- Retry-aware HTTP integration tuned for Salesforce REST endpoints.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_salesforce
```

### uv (project)

```bash
uv add swarmauri_auth_idp_salesforce
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_salesforce
```

## Usage

### Authorization Code logins

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_salesforce import SalesforceOAuth20Login

login = SalesforceOAuth20Login(
    base_url="https://login.salesforce.com",
    client_id="salesforce-client-id",
    client_secret=SecretStr("salesforce-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

# Optional discovery cache when running without network access.
login.discovery_cache = {
    "authorization_endpoint": "https://login.salesforce.com/services/oauth2/authorize",
    "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
    "userinfo_endpoint": "https://login.salesforce.com/services/oauth2/userinfo",
}

async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Redirect the browser to `auth["url"]`, then capture the callback `code` and `state`.
    # Later, call `login.exchange_and_identity(code, state)` inside your callback handler.

asyncio.run(run_flow())
```

### Workflow Summary

1. Call `auth_url()` and redirect the browser to the returned URL.
2. Persist the `state` and verify it during the callback handler.
3. Exchange the authorization code through `exchange_and_identity()` to obtain tokens and profile metadata.

### Server-to-server JWT bearer tokens

```python
import asyncio
from pydantic import SecretStr
from swarmauri_auth_idp_salesforce import SalesforceOAuth20AppClient

client = SalesforceOAuth20AppClient(
    token_endpoint="https://login.salesforce.com/services/oauth2/token",
    client_id="connected-app-id",
    user="integration.user@example.com",
    private_key_pem=SecretStr("-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"),
)

async def fetch_token() -> None:
    access_token = await client.access_token()
    print(access_token)

asyncio.run(fetch_token())
```

Use `SalesforceOAuth21AppClient` when your integration manages keys as JWKs, or
`SalesforceOIDC10AppClient` to discover tenant-specific endpoints before
requesting JWT bearer tokens.

## Entry Points

- `swarmauri.auth_idp:SalesforceOAuth20AppClient`
- `swarmauri.auth_idp:SalesforceOAuth20Login`
- `swarmauri.auth_idp:SalesforceOAuth21AppClient`
- `swarmauri.auth_idp:SalesforceOAuth21Login`
- `swarmauri.auth_idp:SalesforceOIDC10AppClient`
- `swarmauri.auth_idp:SalesforceOIDC10Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
