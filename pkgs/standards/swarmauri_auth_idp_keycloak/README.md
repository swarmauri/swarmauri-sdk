![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_keycloak/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_keycloak" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_keycloak/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_keycloak.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_keycloak/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_keycloak" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_keycloak/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_keycloak" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_keycloak/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_keycloak?label=swarmauri_auth_idp_keycloak&color=green" alt="PyPI - swarmauri_auth_idp_keycloak"/></a>
</p>

---

# Swarmauri Auth IDP Keycloak

Keycloak OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers packaged for Swarmauri deployments.

## Features

- PKCE-enabled Authorization Code flows that integrate with Keycloak realm issuers.
- Discovery-driven OAuth 2.1/OIDC login that validates ID tokens against realm JWKS.
- UserInfo enrichment for deployments that require normalized profile payloads.
- Retry-aware HTTP integration tuned for Keycloak endpoints.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_keycloak
```

### uv (project)

```bash
uv add swarmauri_auth_idp_keycloak
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_keycloak
```

## Usage

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_keycloak import KeycloakOAuth20Login

login = KeycloakOAuth20Login(
    issuer="https://kc.example.com/realms/myrealm",
    client_id="keycloak-client-id",
    client_secret=SecretStr("keycloak-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

# Optional: preload discovery metadata when running outside your Keycloak instance.
login.discovery_cache = {
    "authorization_endpoint": "https://kc.example.com/realms/myrealm/protocol/openid-connect/auth",
    "token_endpoint": "https://kc.example.com/realms/myrealm/protocol/openid-connect/token",
    "userinfo_endpoint": "https://kc.example.com/realms/myrealm/protocol/openid-connect/userinfo",
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

## Entry Points

- `swarmauri.auth_idp:KeycloakOAuth20Login`
- `swarmauri.auth_idp:KeycloakOAuth21Login`
- `swarmauri.auth_idp:KeycloakOIDC10Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
