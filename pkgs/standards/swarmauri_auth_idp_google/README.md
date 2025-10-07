![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_google/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_google" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_google/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_google.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_google/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_google" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_google/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_google" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_google/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_google?label=swarmauri_auth_idp_google&color=green" alt="PyPI - swarmauri_auth_idp_google"/></a>
</p>

---

# Swarmauri Auth IDP Google

Google OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers packaged for Swarmauri deployments.

## Features

- PKCE-enabled Authorization Code flows with HMAC-signed state payloads.
- Discovery-driven OAuth 2.1/OIDC login that validates ID tokens and nonces.
- Profile hydration via Google UserInfo endpoints for normalized downstream payloads.
- Retry-aware HTTP integration tuned for Google Identity services.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_google
```

### uv (project)

```bash
uv add swarmauri_auth_idp_google
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_google
```

## Usage

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_google import GoogleOAuth20Login

login = GoogleOAuth20Login(
    client_id="google-client-id",
    client_secret=SecretStr("google-client-secret"),
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

## Entry Points

- `swarmauri.auth_idp:GoogleOAuth20Login`
- `swarmauri.auth_idp:GoogleOAuth21Login`
- `swarmauri.auth_idp:GoogleOIDC10Login`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
