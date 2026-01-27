![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitlab/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_gitlab" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_gitlab/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_gitlab.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitlab/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_gitlab" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitlab/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_gitlab" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_gitlab/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_gitlab?label=swarmauri_auth_idp_gitlab&color=green" alt="PyPI - swarmauri_auth_idp_gitlab"/></a>
</p>

---

# Swarmauri Auth IDP GitLab

GitLab OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers and app clients packaged for Swarmauri deployments.

## Features

- Authorization Code flows with PKCE and HMAC-signed state payloads for GitLab SaaS or self-managed.
- Discovery-driven OAuth 2.1 & OIDC login that validates ID tokens and hydrates profile details.
- Client credentials helpers that support shared secrets and JWT assertions.
- Retry-aware HTTP integration with GitLab REST API v4 and OIDC endpoints.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_gitlab
```

### uv (project)

```bash
uv add swarmauri_auth_idp_gitlab
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_gitlab
```

## Usage

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_gitlab import GitLabOAuth20Login

login = GitLabOAuth20Login(
    base_url="https://gitlab.example",
    client_id="gitlab-client-id",
    client_secret=SecretStr("gitlab-client-secret"),
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
4. Instantiate `GitLabOAuth21AppClient` or `GitLabOIDC10AppClient` to fetch service tokens for background jobs.

## Entry Points

- `swarmauri.auth_idp:GitLabOAuth20Login`
- `swarmauri.auth_idp:GitLabOAuth21Login`
- `swarmauri.auth_idp:GitLabOIDC10Login`
- `swarmauri.auth_idp:GitLabOAuth20AppClient`
- `swarmauri.auth_idp:GitLabOAuth21AppClient`
- `swarmauri.auth_idp:GitLabOIDC10AppClient`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
