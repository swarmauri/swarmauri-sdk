# auto_authn Overview

## Router Endpoint Modules
- `rfc7591.py` – client registration endpoint
- `rfc9126.py` – pushed authorization request endpoint
- `rfc8628.py` – device authorization endpoint
- `rfc8932.py` – enhanced authorization server metadata endpoint
- `rfc8414.py` – OAuth 2.0 authorization server metadata endpoint
- `rfc7009.py` – token revocation endpoint
- `rfc8693.py` – token exchange endpoint
- `oidc_userinfo.py` – OpenID Connect `/userinfo` endpoint
- `oidc_discovery.py` – OpenID discovery endpoints
- `routers/auth_flows.py` – aggregates authorization routers
- `routers/authz/__init__.py` – authorization routes (token, introspection, etc.)
- `routers/crud.py` – AutoAPI-generated CRUD router for ORM models

## Schema Modules
- `routers/schemas.py` – request/response models for auth flows
- `rfc7591.py` – `ClientMetadata` for dynamic client registration
- `rfc8628.py` – `DeviceAuthIn`, `DeviceAuthOut`, and `DeviceGrantForm`
- `rfc9396.py` – `AuthorizationDetail` for rich authorization requests
- `rfc8693.py` – `TokenType`, `TokenExchangeRequest`, and `TokenExchangeResponse`
- `orm/` modules – SQLAlchemy models (`Tenant`, `User`, `Client`, `Service`, `ApiKey`, `ServiceKey`, `AuthSession`, `AuthCode`, `DeviceCode`, `RevokedToken`, `PushedAuthorizationRequest`)

### Persistence vs. Virtual Schemas
- **Persistent**: ORM models from `orm/` (listed above)
- **Virtual**: Pydantic/in-memory classes such as `RegisterIn`, `TokenPair`, `ClientMetadata`, `DeviceAuthIn`, `DeviceAuthOut`, `DeviceGrantForm`, `AuthorizationDetail`, `TokenType`, `TokenExchangeRequest`, and `TokenExchangeResponse`

## Crypto Modules
- `crypto.py` – bcrypt password hashing and Ed25519 key management
- `rfc7515.py` – JSON Web Signature helpers
- `rfc7516.py` – JSON Web Encryption helpers
- `rfc7517.py` – loading signing and public JWKs
- `rfc7518.py` – supported JOSE algorithms list
- `rfc7519.py` – JWT encode/decode wrappers
- `rfc7638.py` – JWK thumbprint generation and verification
- `rfc7800.py` – confirmation claim and proof-of-possession utilities
- `rfc8291.py` – AES-128-GCM encryption/decryption for push messages
- `rfc8037.py` – EdDSA signing and verification helpers
- `rfc8705.py` – certificate thumbprint and binding validation
- `rfc9449_dpop.py` – DPoP proof creation and verification

## ORM Tables, Columns, and Operations
| Table | Acols (stored columns) | Vcols (virtual/relationships) | Default Ops | Additional Ops | Hook Context |
|-------|------------------------|-------------------------------|-------------|----------------|--------------|
| `Tenant` | `id`, `slug`, `created_at`, `updated_at`, `name`, `email` | — | create, read, update, delete, list | — | — |
| `User` | `id`, `created_at`, `updated_at`, `tenant_id`, `username`, `email`, `password_hash`, `is_active` | `api_keys` relationship | create, read, update, delete, list | register | `hash_pw` pre-create/pre-update for password hashing |
| `Client` | `id`, `created_at`, `updated_at`, `tenant_id`, `client_secret_hash`, `redirect_uris`, `is_active` | — | create, read, update, delete, list | dynamic client registration (`rfc7591`) | optional `hash_client_secret` hook |
| `Service` | `id`, `created_at`, `updated_at`, `tenant_id`, `is_active`, `name` | `service_keys` relationship | create, read, update, delete, list | — | `encrypt_service_key` if needed |
| `ApiKey` | `id`, `created_at`, `last_used_at`, `valid_from`, `valid_to`, `label`, `digest`, `user_id` | `user` relationship | create, read, update, delete, list | generate/return raw key | pre-create `generate_api_key`, post-create `return_raw_key` |
| `ServiceKey` | same as `ApiKey` plus `service_id` | `service` relationship | create, read, update, delete, list | — | similar hooks as `ApiKey` |
| `AuthSession` | `id`, `user_id`, `tenant_id`, `username`, `auth_time`, `created_at`, `updated_at` | — | create, read, update, delete, list | login, logout | credential verification on login |
| `AuthCode` | `code`, `user_id`, `tenant_id`, `client_id`, `redirect_uri`, `code_challenge`, `nonce`, `scope`, `expires_at`, `claims`, `created_at`, `updated_at` | — | create, read, update, delete, list | — | — |
| `DeviceCode` | `device_code`, `user_code`, `client_id`, `expires_at`, `interval`, `authorized`, `user_id`, `tenant_id`, `created_at`, `updated_at` | — | create, read, update, delete, list | device authorization | `issue_device_code`, `notify_user_agent` hooks when persisted |
| `RevokedToken` | `token`, `created_at`, `updated_at` | — | create, read, update, delete, list | revoke | `store_revoked_token` pre-create |
| `PushedAuthorizationRequest` | `request_uri`, `params`, `expires_at`, `created_at`, `updated_at` | — | create, read, update, delete, list | pushed authorization request | `persist_par_request` pre-create |

### Notes on Operations
- **op_alias**: no explicit overrides; CRUD uses default verbs.
- **schema_ctx**: use when virtual fields (e.g., `password`) cannot map directly to persistent columns.
- **Lifecycle hooks**: attach callables like `_pwd_backend.verify`, `_jwt.encode`, or custom crypto/providers to appropriate `pre_*` or `post_*` phases.

## Hook Context Examples
| Endpoint | Lifecycle Hook | Purpose |
|----------|----------------|---------|
| `POST /register` | `pre_create` → `hash_pw` | Hash incoming password before persisting `User` record |
| `POST /login` | `pre_read` → `_pwd_backend.verify` | Verify password before issuing tokens |
| CRUD `ApiKey` | `pre_create` → `generate_api_key`, `post_create` → `return_raw_key` | Create digest and return plaintext key |
| `POST /token` | `pre_read`/`post_create` → `_pwd_backend.verify`, `_jwt.encode` | Validate client secrets and sign issued tokens |
| `POST /revoke` | `pre_create` → `store_revoked_token` | Persist revoked tokens to `RevokedToken` table |
| `POST /device_authorization` | `pre_create`/`post_create` → `issue_device_code`, `notify_user_agent` | Generate and optionally persist device/user codes |
| `POST /par` | `pre_create` → `persist_par_request` | Store pushed authorization request |
| `POST /token/exchange` | `post_create` → `_jwt.encode` | Sign exchanged tokens |
| `GET /userinfo` | `post_read` → `_jwt.encode` (optional) | Optionally sign the userinfo response |

