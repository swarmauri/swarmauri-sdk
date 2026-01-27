![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_github/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_github" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_github/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_github.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_github/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_github" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_github/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_github" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_github/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_github?label=swarmauri_auth_idp_github&color=green" alt="PyPI - swarmauri_auth_idp_github"/></a>
</p>

---

# Swarmauri Auth IDP GitHub

GitHub OAuth 2.0 / 2.1 logins and installation token helpers packaged for Swarmauri deployments.

## Features

- PKCE-enabled Authorization Code flows with HMAC-signed state payloads.
- Token exchange helpers that return normalized identity payloads for downstream services.
- Profile enrichment that fetches the authenticated user's primary verified email.
- Installation access tokens for GitHub Apps with automatic caching and retry-aware HTTP.
- ComponentBase-compatible models that register under `swarmauri.auth_idp` entry points.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_github
```

### uv (project)

```bash
uv add swarmauri_auth_idp_github
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_github
```

## Usage

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_github import GitHubOAuth21Login

login = GitHubOAuth21Login(
    client_id="github-client-id",
    client_secret=SecretStr("github-client-secret"),
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
4. Instantiate `GitHubOAuth21AppClient` to fetch GitHub App installation tokens when acting on behalf of repositories.

## Entry Points

- `swarmauri.auth_idp:GitHubOAuth20Login`
- `swarmauri.auth_idp:GitHubOAuth21Login`
- `swarmauri.auth_idp:GitHubOAuth20AppClient`
- `swarmauri.auth_idp:GitHubOAuth21AppClient`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
