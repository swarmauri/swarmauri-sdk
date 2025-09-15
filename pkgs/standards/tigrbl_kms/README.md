![Tigrbl Logo](../../../assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_kms/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_kms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_kms.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_kms/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_kms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_kms/">
        <img src="https://img.shields.io/pypi/l/tigrbl_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_kms/">
        <img src="https://img.shields.io/pypi/v/tigrbl_kms?label=tigrbl_kms&color=green" alt="PyPI - tigrbl_kms"/></a>
</p>

---

# Tigrbl KMS 🔐

> A lightweight key management service powered by FastAPI and the Tigrbl engine.

## ✨ Features

- 🔑 Manage symmetric keys with versioning and rotation.
- 🚀 Ships with a ready-to-run FastAPI application.
- 🤖 Extensible through `swarmauri_crypto_*` plugins.
- 📦 Backed by SQLAlchemy and Pydantic models.

## 🚀 Quick Start

### Run the built-in app

Tigrbl KMS ships a FastAPI application at `tigrbl_kms.app:app`. Configure the database URL if needed (defaults to `sqlite+aiosqlite:///./kms.db`) and launch it with uvicorn:

```bash
export KMS_DATABASE_URL=sqlite+aiosqlite:///./kms.db
uv run --package tigrbl_kms --directory pkgs/standards/tigrbl_kms \
  uvicorn tigrbl_kms.app:app --host 127.0.0.1 --port 8000 --reload
```

### Verify

Once the service starts, you can verify it is running:

```bash
curl http://127.0.0.1:8000/system/healthz
```

The endpoint returns `{"ok": true}` when deployment succeeds.

## 🛠️ Build a custom app

You can construct a bespoke Tigrbl KMS service by creating your own `TigrblApp` and adding the KMS resources:

```python
from tigrbl import TigrblApp
from tigrbl.engine import engine
from tigrbl_kms.orm import Key, KeyVersion
from swarmauri_standard.key_providers import InMemoryKeyProvider
from swarmauri_crypto_pgp import PgpCrypto  # swap for any swarmauri_crypto_* plugin

db = engine("sqlite+aiosqlite:///./kms.db")
crypto = PgpCrypto()
key_provider = InMemoryKeyProvider()

async def add_services(ctx):
    ctx["crypto"] = crypto
    ctx["key_provider"] = key_provider

app = TigrblApp(engine=db, api_hooks={"*": {"PRE_TX_BEGIN": [add_services]}})
app.include_models([Key, KeyVersion], base_prefix="/kms")
app.mount_jsonrpc(prefix="/kms/rpc")
app.attach_diagnostics(prefix="/system")

@app.on_event("startup")
async def startup():
    await app.initialize()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
```

The `PgpCrypto` instance above can be replaced with any other `swarmauri_crypto_*` plugin such as `swarmauri_crypto_paramiko` or `swarmauri_crypto_rust`.

## 🔒 Create a key and encrypt data

In another terminal, create a key:

```bash
curl -s -X POST http://127.0.0.1:8000/kms/Key \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","algorithm":"AES256_GCM"}'
```

Example response:

```json
{"id":"5e454eb6-7739-453b-9aee-21d60032a773","name":"demo","algorithm":"AES256_GCM","status":"enabled","primary_version":1}
```

Encrypt some data with the key (the plaintext must be base64-encoded):

```bash
PLAINTEXT=$(echo -n 'hello world' | base64)
curl -s -X POST http://127.0.0.1:8000/kms/Key/5e454eb6-7739-453b-9aee-21d60032a773/encrypt \
  -H "Content-Type: application/json" \
  -d "{\"plaintext_b64\":\"$PLAINTEXT\"}"
```

Sample output:

```json
{"kid":"5e454eb6-7739-453b-9aee-21d60032a773","version":1,"alg":"AES256_GCM","nonce_b64":"bg==","ciphertext_b64":"ZGxyb3cgb2xsZWg=","tag_b64":"dA=="}
```

The ciphertext is base64 encoded and can be decrypted with the corresponding `decrypt` endpoint.

## 📄 License

This project is licensed under the terms of the [Apache 2.0](LICENSE) license.
