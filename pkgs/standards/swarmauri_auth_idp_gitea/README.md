![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitea/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_gitea" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_gitea/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_gitea.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitea/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_gitea" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitea/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_gitea" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitea/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_gitea?label=swarmauri_auth_idp_gitea&color=green" alt="PyPI - swarmauri_auth_idp_gitea"/></a>
</p>

---

# Swarmauri Auth IDP Gitea

Gitea OAuth 2.0, OAuth 2.1, and OIDC 1.0 login and app-client flows packaged for the Swarmauri ecosystem.

## Features

- PKCE-enabled authorization code flows with signed state payloads and resilient retries.
- Automatic profile enrichment using the Gitea REST API with email fallbacks.
- Optional private-key JWT client authentication for high-assurance machine-to-machine use.
- OIDC support that validates ID tokens and gracefully falls back to UserInfo claims.
- ComponentBase-registered classes for discovery through Swarmauri plugin entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_gitea
```

### uv (project)

```bash
uv add swarmauri_auth_idp_gitea
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_gitea
```

## Usage

Instantiate the login classes with your Gitea base URL, client credentials, and redirect URI.
Persist the signed state returned by `auth_url` and supply it to the exchange step.

```python
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_gitea import GiteaOAuth21Login

login = GiteaOAuth21Login(
    base_url="https://gitea.example.com",
    client_id="example-client-id",
    client_secret=SecretStr("example-secret"),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# Within an async context:
# auth_payload = await login.auth_url()
# identity = await login.exchange_and_identity(code, auth_payload["state"])
print(login.client_id)
```

### Expected Workflow

1. Call `auth_url()` and redirect the user agent to Gitea's authorization endpoint.
2. Persist the returned state and verify it during the callback to prevent tampering.
3. Call `exchange_and_identity()` (or `exchange()` for the OIDC login) to normalize user claims.
4. Use the normalized payload to create sessions, audit events, or downstream tokens.

App client classes expose `access_token()` for service-to-service integrations using either
client secrets or private-key JWT assertions.

## Entry Points

The distribution registers the following entry points:

- `swarmauri.auth_idp:GiteaOAuth20Login`
- `swarmauri.auth_idp:GiteaOAuth21Login`
- `swarmauri.auth_idp:GiteaOIDC10Login`
- `swarmauri.auth_idp:GiteaOAuth20AppClient`
- `swarmauri.auth_idp:GiteaOAuth21AppClient`
- `swarmauri.auth_idp:GiteaOIDC10AppClient`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
covering development workflow, testing, and coding standards.
