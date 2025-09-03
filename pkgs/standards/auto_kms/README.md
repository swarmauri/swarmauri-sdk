## Auto KMS

Auto KMS provides a lightweight key management service built on FastAPI. 

### Deploy

Run the service with the provided CLI:

```bash
uv run --package auto_kms --directory pkgs/standards/auto_kms auto-kms --host 127.0.0.1 --port 8000 --no-reload
```

### Verify

Once the service starts, you can verify it is running:

```bash
curl http://127.0.0.1:8000/system/healthz
```

The endpoint returns `{"ok": true}` when deployment succeeds.

### Create a key and encrypt data

Initialize the SQLite database:

```bash
uv run --package auto_kms --directory pkgs/standards/auto_kms -- python - <<'PY'
from auto_kms.app import engine
from autoapi.v3.orm.tables import Base
import asyncio

async def init():
    sqla_engine, _ = engine.raw()
    async with sqla_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init())
PY
```

Start a demo server that injects a simple crypto provider:

```bash
uv run --package auto_kms --directory pkgs/standards/auto_kms -- python - <<'PY'
import uvicorn
from auto_kms.app import app
from types import SimpleNamespace

class DummyCrypto:
    async def encrypt(self, *, kid, plaintext, alg, aad=None, nonce=None):
        return SimpleNamespace(nonce=b'n', ct=plaintext[::-1], tag=b't', version=1, alg=alg)

    async def decrypt(self, *, kid, ciphertext, nonce, tag=None, aad=None, alg=None):
        return ciphertext[::-1]

@app.middleware("http")
async def add_crypto(request, call_next):
    request.state.crypto = DummyCrypto()
    return await call_next(request)

uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
PY
```

In another terminal, create a key:

```bash
curl -s -X POST http://127.0.0.1:8000/kms/Key \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","algorithm":"AES256_GCM"}'
```

Example response:

```
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

```
{"kid":"5e454eb6-7739-453b-9aee-21d60032a773","version":1,"alg":"AES256_GCM","nonce_b64":"bg==","ciphertext_b64":"ZGxyb3cgb2xsZWg=","tag_b64":"dA=="}
```

The ciphertext is base64 encoded and can be decrypted with the corresponding `decrypt` endpoint.
