![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_okta" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_okta/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_okta.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_okta" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_okta" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_okta?label=swarmauri_auth_idp_okta&color=green" alt="PyPI - swarmauri_auth_idp_okta"/></a>
</p>

---

# Swarmauri Auth IDP Okta

Okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers packaged for Swarmauri deployments.

## Features

- PKCE-enabled Authorization Code flows that integrate with Okta authorization servers.
- Machine-to-machine app clients for Okta OAuth 2.0, OAuth 2.1 (private key JWT), and OIDC 1.0.
- Discovery-driven OAuth 2.1/OIDC login that verifies ID tokens using Okta JWKS.
- UserInfo enrichment for deployments that require full user profile hydration.
- Retry-aware HTTP integration tuned for Okta endpoints.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_okta
```

### uv (project)

```bash
uv add swarmauri_auth_idp_okta
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_okta
```

## Usage

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_okta import OktaOAuth20Login

login = OktaOAuth20Login(
    issuer="https://example.okta.com/oauth2/default",
    client_id="okta-client-id",
    client_secret=SecretStr("okta-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

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

### Server-to-server client credentials

```python
import asyncio
from pydantic import SecretStr
from swarmauri_auth_idp_okta import OktaOAuth20AppClient

client = OktaOAuth20AppClient(
    issuer="https://example.okta.com/oauth2/default",
    client_id="machine-client-id",
    client_secret=SecretStr("machine-client-secret"),
)

async def fetch_token() -> None:
    token = await client.access_token(scope="customScope")
    print(token)

asyncio.run(fetch_token())
```

Use `OktaOAuth21AppClient` when the integration should authenticate with
`private_key_jwt`, or `OktaOIDC10AppClient` to rely on discovery metadata for
tenant-specific token endpoints.

## Entry Points

- `swarmauri.auth_idp:OktaOAuth20AppClient`
- `swarmauri.auth_idp:OktaOAuth20Login`
- `swarmauri.auth_idp:OktaOAuth21AppClient`
- `swarmauri.auth_idp:OktaOAuth21Login`
- `swarmauri.auth_idp:OktaOIDC10AppClient`
- `swarmauri.auth_idp:OktaOIDC10Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
