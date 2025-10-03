# idp-clients

Production-ready OAuth2/OIDC app clients and user login modules.

## Contents
- Base app clients (`idp_clients/base/*`) for OAuth 2.0, OAuth 2.1-aligned, and OIDC 1.0 discovery.
- Google Identity Services user login modules (OIDC 1.0, OAuth2.1-aligned, OAuth2.0).
- AWS IAM Workforce (Identity Center) user login modules for OAuth 2.0 / 2.1-aligned.
  - Note: OIDC 1.0 user login is not supported by AWS IAM Identity Center (no ID tokens).

## Python
- Python 3.10+ recommended.
- `pip install -e .` to develop locally.

## Security defaults
- PKCE + HMAC-signed state with TTL.
- Timeouts, retries, exponential backoff.
- No implicit/password flows; optional private_key_jwt for client auth.



## New vendors in this build
- **Azure AD (Microsoft Entra ID)**: `azure_ad/*` — OIDC 1.0, OAuth 2.0, OAuth 2.1-aligned user login flows.
- **GitHub**: `github/*` — GitHub App client (server-to-server), GitHub App OAuth (user), and classic GitHub OAuth (read:user user:email).
