# Auto Authn v2 Server

This server provides a FastAPI implementation of the Auto AuthN identity provider. It exposes OAuth2/OpenID Connect compliant endpoints.

## Deployment

1. **Install** the package and its optional extras:
   ```bash
   pip install auto_authn[sqlite]  # or auto_authn[postgres]
   ```
2. **Run** the application with Uvicorn:
   ```bash
   uvicorn auto_authn.app:app --reload
   ```
3. **Configure** runtime settings via environment variables:
   - `DATABASE_URL` – database connection string (e.g. `sqlite+aiosqlite:///./authn.db`).
   - `AUTHN_ISSUER` – issuer URL used in discovery documents.

## Administration

- `GET /healthz` returns service liveness status.
- `GET /methodz` exposes build metadata for operational checks.
- `GET /.well-known/openid-configuration` publishes OIDC discovery data.
- `GET /.well-known/jwks.json` exposes the JSON Web Key Set for token verification.

## Usage

### Health check

```python
from fastapi.testclient import TestClient
from auto_authn.app import app

client = TestClient(app)
assert client.get("/healthz").json() == {"status": "alive"}
```

### Password grant (RFC 6749)

```python
import uuid
from fastapi.testclient import TestClient
from auto_authn.app import app

client = TestClient(app)

slug = f"tenant-{uuid.uuid4().hex[:6]}"
client.post(
    "/tenant",
    json={"slug": slug, "name": "Example", "email": "ops@example.com"},
)
client.post(
    "/register",
    json={
        "tenant_slug": slug,
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecretPwd123",
    },
)
tokens = client.post(
    "/token",
    data={
        "grant_type": "password",
        "username": "alice",
        "password": "SecretPwd123",
    },
).json()
```

### Refresh token (RFC 6749)

```python
refreshed = client.post(
    "/token/refresh", json={"refresh_token": tokens["refresh_token"]}
).json()
```

### RP-initiated logout

```python
client.post("/logout", json={"id_token_hint": tokens["id_token"]})
```

### Token revocation (RFC 7009)

```python
import os
from importlib import reload
from fastapi.testclient import TestClient
import auto_authn.app as app_module

os.environ["AUTO_AUTHN_ENABLE_RFC7009"] = "1"
reload(app_module)

client = TestClient(app_module.app)
client.post("/revoke", data={"token": "deadbeef"})
```

The snippets demonstrate programmatic access to the server and showcase RFC-compliant
workflows using FastAPI's `TestClient` for testing or integration purposes.
