![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_auth_idp_cognito/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_cognito" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_cognito/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_auth_idp_cognito.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_cognito/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_auth_idp_cognito" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_cognito/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_cognito" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_cognito/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_cognito?label=swarmauri_auth_idp_cognito&color=green" alt="PyPI - swarmauri_auth_idp_cognito"/></a>
</p>

---

# Swarmauri Auth IDP Cognito

AWS Cognito OAuth 2.0, OAuth 2.1, and OIDC 1.0 login and app-client flows packaged for the Swarmauri ecosystem.

## Features

- PKCE-enabled authorization code logins with signed state payloads to prevent tampering.
- Automatic discovery of Cognito endpoints with resilient HTTP retry semantics.
- ID token verification against Cognito JWKS with graceful fallback to the UserInfo endpoint.
- Machine-to-machine app clients supporting shared secrets or JWT-based client assertions.
- ComponentBase-registered classes for seamless Swarmauri plugin discovery and configuration.

## Installation

### pip

```bash
pip install swarmauri_auth_idp_cognito
```

### uv (project)

```bash
uv add swarmauri_auth_idp_cognito
```

### uv (environment)

```bash
uv pip install swarmauri_auth_idp_cognito
```

## Usage

Instantiate the login classes with your Cognito issuer, app client credentials, and redirect URI.
Persist the returned state between `auth_url` and `exchange*` calls to prevent replay attacks.

```python
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_cognito import CognitoOAuth21Login

login = CognitoOAuth21Login(
    issuer="https://example-domain.auth.us-east-1.amazoncognito.com",
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

1. Call `auth_url()` and redirect the user agent to the returned authorization URL.
2. Persist the state value and later validate it when Cognito posts back to your callback.
3. Call `exchange_and_identity()` (or `exchange()` for the OIDC login) to normalize identity claims.
4. Use the normalized payload to provision sessions, issue downstream tokens, or audit login activity.

App client classes expose the same `access_token` coroutine to support background services
and machine-to-machine integrations.

## Entry Points

The distribution registers the following entry points:

- `swarmauri.auth_idp:CognitoOAuth20Login`
- `swarmauri.auth_idp:CognitoOAuth21Login`
- `swarmauri.auth_idp:CognitoOIDC10Login`
- `swarmauri.auth_idp:CognitoOAuth20AppClient`
- `swarmauri.auth_idp:CognitoOAuth21AppClient`
- `swarmauri.auth_idp:CognitoOIDC10AppClient`

## Contributing

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md),
including development workflow, testing, and coding standards.
