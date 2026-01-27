![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_apple/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_apple" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_apple/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_apple.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_apple/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_apple" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_apple/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_apple" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_apple/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_apple?label=swarmauri_auth_idp_apple&color=green" alt="PyPI - swarmauri_auth_idp_apple"/></a>
</p>

---

# Swarmauri Auth IDP Apple

Apple Sign-In OAuth 2.0, OAuth 2.1, and OIDC 1.0 flows packaged for the Swarmauri ecosystem.

## Features

- PKCE-enabled authorization code flows with signed state payloads to prevent tampering.
- Automatic OpenID Connect discovery and JWKS verification for ID token integrity.
- Reusable async HTTP client with retry and jitter to tolerate transient Apple API issues.
- Typed, ComponentBase-derived classes that register with Swarmauri plugin discovery.
- Explicit app-client stubs that document unsupported Apple client credentials grants.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_apple
```

### uv (project)

```bash
uv add swarmauri_auth_idp_apple
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_apple
```

## Usage

The login classes expose the same asynchronous interface as the core `IOAuth*Login`
contracts. Instantiate them with your Apple developer credentials, persist the `state`
returned by `auth_url`, and provide it back during the exchange step.

```python
from pydantic import SecretBytes
from swarmauri_auth_idp_apple import AppleOAuth21Login

login = AppleOAuth21Login(
    team_id="ABCD123456",
    key_id="XYZ7890",
    client_id="com.example.web",
    private_key_pem=SecretBytes(b"""-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"""),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# In your application, call `await login.auth_url()` to initiate the flow and
# `await login.exchange_and_identity(...)` inside an async context.
print(login.client_id)
```

### Expected Workflow

1. Call `auth_url()` and redirect the user-agent to the returned URL.
2. Persist the `state` for later validation (cookie, session, encrypted store, etc.).
3. On the redirect back to your service, validate the returned `state` and `code`
   by calling `exchange_and_identity()` (or `exchange()` for the OIDC login).
4. Consume the normalized identity payload to provision sessions or tokens.

The package includes app-client classes which raise `NotImplementedError` to highlight
that Apple does not support generic client credential grants for Sign in with Apple.

## Entry Points

The distribution registers the following entry points:

- `swarmauri.auth_idp:AppleOAuth20Login`
- `swarmauri.auth_idp:AppleOAuth21Login`
- `swarmauri.auth_idp:AppleOIDC10Login`
- `swarmauri.auth_idp:AppleOAuth20AppClient`
- `swarmauri.auth_idp:AppleOAuth21AppClient`
- `swarmauri.auth_idp:AppleOIDC10AppClient`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.
