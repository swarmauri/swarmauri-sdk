# Auto‑AuthN  IdP; Multi‑Tenant OpenID‑Connect Provider

**Auto‑AuthN** is a batteries‑included, async, SQL‑backed OpenID‑Connect 1.0 / OAuth 2.1
Identity‑Provider written in Python 3.11+.  
It is designed for SaaS vendors who need per‑customer (tenant) isolation while
running a single scalable cluster.

---

## ✨ Features

| Capability | Detail |
|------------|--------|
| **Multi‑tenant** | Per‑tenant issuer URL, JWKS, user & client tables. |
| **Secure crypto** | RSA 2048 bits (RS256) signing; helpers for seamless key rotation. |
| **Async stack** | FastAPI + SQLAlchemy 2.0 async + pyoidc 2.5. |
| **Password auth** | Bcrypt‑hashed credentials; easy plug‑in for TOTP / SAML / WebAuthn MFA. |
| **Admin CLI** | Create tenants, register clients, rotate keys, seed users. |
| **Device‑Code & PKCE** | Headless + browser flows for CLIs and SPA RPs. |
| **Docker‑friendly** | Single `Dockerfile`, health endpoints, graceful shutdown. |
| **Zero‑hop JWKS** | Public keys served at `/{tenant}/jwks.json` for RP validation. |
| **Extensible** | Everything wired through dependency overrides; swap Postgres, Redis, metrics, … |

---

## 📂 Repository Layout (src/)

```

auth\_authn\_idp/
├── config.py      # Env‑driven settings (pydantic‑settings)
├── db.py          # Async engine + session factory
├── models.py      # ORM tables: Tenant, User, Client
├── crypto.py      # RSA key generation & rotation helpers
├── authn.py       # Username/password backend (pyoidc bridge)
├── provider.py    # Provider factory + FastAPI routers
├── main.py        # Uvicorn entry‑point
└── cli/           # Typer admin commands (tenants/clients/users/keys)

````

---

## 🚀 Quick Start (SQLite, no TLS; **dev only**)

```bash

pip install -e ".[sqlite]"     # editable install + SQLite driver

# Initialise DB + seed default tenant
export AUTO_AUTHN_DATABASE_URL="sqlite+aiosqlite:///./idp.db"
export AUTO_AUTHN_PUBLIC_URL="http://localhost:8000"
auto-authn tenants create default --issuer http://localhost:8000/default

# Run
uvicorn auto_authn.main:app --reload
````

Visit:

```
GET http://localhost:8000/default/.well-known/openid-configuration
```

---

## ⚙️ Configuration Reference

| Env var (prefix `AUTO_AUTHN_`) | Default                               | Description                                                            |
| ------------------------------ | ------------------------------------- | ---------------------------------------------------------------------- |
| `DATABASE_URL`                 | `sqlite+aiosqlite:///./auto_authn.db` | Async SQLAlchemy URL. Use Postgres in prod (`postgresql+asyncpg://…`). |
| `REDIS_URL`                    | `redis://localhost:6379/0`            | Redis for pub/sub or session store (optional).                         |
| `PUBLIC_URL`                   | **required in prod**                  | External URL shown in discovery (`issuer`).                            |
| `LOG_LEVEL`                    | `INFO`                                | `DEBUG`, `INFO`, `WARNING`, …                                          |
| `SESSION_SYM_KEY`              | `ChangeMeNow123456`                   | 16/24/32 byte AES key for session cookies.                             |
| `CORS_ORIGINS`                 | *empty*                               | Comma‑sep list of SPA origins.                                         |

See `auto_authn/config.py` for the full schema.

---

## 📝 Database Migration

```bash
pip install alembic
alembic upgrade head
```

The shipped alembic environment auto‑loads `auto_authn.models.Base.metadata`.

---

## 🔑 Tenant & Client Lifecycle

```bash
# 1. create tenant (issuer -> https://login.acme.localhost)
auto-authn tenants create acme \
    --issuer https://login.acme.localhost \
    --name "Acme Corp"

# 2. add user (bcrypt hashed password)
auto-authn users add --tenant acme --username alice --email a@acme.com

# 3. register relying‑party / client
auto-authn clients register \
    --tenant acme \
    --client-id service-acme \
    --redirect-uris https://app.service.io/auth/callback/acme \
    --secret $(openssl rand -hex 24)
```

---

## 🔒 Key Rotation

Rotate keys for all tenants older than 90 days:

```bash
auto-authn tenants rotate-keys --grace 7776000   # 90d
```

This:

1. Generates a new RSA 2048 key.
2. Appends it to the tenant’s JWKS (`kid` chosen from the RSA thumb‑print).
3. Prunes any signing key older than `--grace` seconds.

Relying parties fetch the new public key via `jwks.json` and require **no downtime**.

---

## 🌐 OIDC Endpoints

| HTTP Method & Path                                | Description                                                      |
| ------------------------------------------------- | ---------------------------------------------------------------- |
| `GET  /{tenant}/.well-known/openid-configuration` | Standard discovery document (issuer, endpoints, JWKS URI).       |
| `GET  /{tenant}/jwks.json`                        | Public keys (RS256).                                             |
| `GET  /{tenant}/authorize`                        | Authorization Code + PKCE endpoint.                              |
| `POST /{tenant}/token`                            | Code ↦ token exchange (`application/x-www-form-urlencoded`).     |
| `GET  /{tenant}/userinfo`                         | Protected resource, returns claims (email, preferred\_username). |
| `POST /password-login` *(optional)*               | Direct password grant (returns session cookie).                  |

---

## ▶️ Integrating a Client (RP) – Python example

```python
from authlib.integrations.httpx_client import AsyncOAuth2Client
import asyncio, httpx

TENANT = "acme"
ISS = f"https://login.{TENANT}.localhost"
CLIENT_ID = "service-acme"
CLIENT_SECRET = "********"

async def main():
    async with httpx.AsyncClient() as http:
        discovery = (await http.get(f"{ISS}/.well-known/openid-configuration")).json()

    oauth = AsyncOAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope="openid profile email",
        redirect_uri="https://app.service.io/auth/callback/acme",
        metadata=discovery,
    )

    auth_url, state = oauth.create_authorization_url(discovery["authorization_endpoint"])
    print("Open browser:", auth_url)

    # ↩️  User authenticates → browser redirects back with ?code=…
    code = input("Enter code from redirect URL: ")

    token = await oauth.fetch_token(
        discovery["token_endpoint"],
        code=code,
        code_verifier=oauth.client_kwargs["code_verifier"],
    )

    # 🔑  Validate ID‑token signature
    print("ID‑token:", token["id_token"])

asyncio.run(main())
```

---

## 🐳 Docker Compose (Postgres + IdP)

```yaml
version: "3.9"
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: idp
      POSTGRES_USER: idp
      POSTGRES_PASSWORD: secret
    volumes: [ "./pg_data:/var/lib/postgresql/data" ]

  idp:
    build: .
    command: uvicorn auto_authn.main:app --host 0.0.0.0 --port 8000
    environment:
      AUTO_AUTHN_DATABASE_URL: postgresql+asyncpg://idp:secret@db/idp
      AUTO_AUTHN_PUBLIC_URL: https://login.localhost
    ports: [ "8000:8000" ]
    depends_on: [ db ]
```

---

## 🧪 Running the Test Suite

```bash
pip install -e ".[dev,sqlite]"
pytest -q
```

---

## 🛠️ Development Tips

* **Live reload**: `uvicorn auto_authn.main:app --reload`.
* **Lint / Format**: `ruff check . && ruff format .`.
* **Type‑check**: `mypy src/ tests/`.

---

## 🔌 Adding MFA (Time‑based OTP)

1. Implement `TOTPAuthn(SQLPasswordAuthn)` in `authn_totp.py`.
2. Register it with higher ACR in `_provider_factory()`:

```python
from oic.utils.authn.authn_context import MULTI_FACTOR
broker.add(MULTI_FACTOR, TOTPAuthn(db, tenant), 20)
```

3. Advertise ACR values in discovery (`acr_values_supported`).

---

## 📈 Production Hardening Checklist

| ✅ | Item                                                             |
| - | ---------------------------------------------------------------- |
| ☐ | Terminate TLS at reverse‑proxy (issuer must be `https://`).      |
| ☐ | Store `SESSION_SYM_KEY` & DB credentials in a secret manager.    |
| ☐ | Point `DATABASE_URL` to Postgres (and configure WAL backups).    |
| ☐ | Use Redis for session DB (swap `SessionDB` implementation).      |
| ☐ | Enable CORS domains for SPA RPs only (never `*`).                |
| ☐ | Run alembic migrations on deploy (CI/CD step).                   |
| ☐ | Schedule `auto-authn tenants rotate-keys` weekly via cron‑job.   |
| ☐ | Enable rate‑limit & bot‑defence middlewares in `middlewares.py`. |

---

> © 2025 Swarmauri