from __future__ import annotations

from fastapi import FastAPI
from autoapi.v2 import AutoAPI, Phase
from autoapi.v2.tables import Base

from .tables.key import Key
from .tables.key_version import KeyVersion

from swarmauri_secret_autogpg import AutoGpgSecretDrive
from swarmauri_crypto_paramiko import ParamikoCrypto


# Build AutoAPI and mount on FastAPI app
api = AutoAPI(
    base=Base,
    include={Key, KeyVersion},
    prefix="/kms",
)


@api.register_hook(Phase.PRE_TX_BEGIN)
async def _stash_ctx(ctx):
    global SECRETS, CRYPTO
    try:
        SECRETS
        CRYPTO
    except NameError:
        SECRETS = AutoGpgSecretDrive()
        CRYPTO = ParamikoCrypto()
    ctx["_kms_secrets"] = SECRETS
    ctx["_kms_crypto"] = CRYPTO


@api.register_hook(Phase.POST_RESPONSE)
async def _finalize_kms_result(ctx):
    if "__kms_result__" in ctx:
        ctx["response"].result = ctx.pop("__kms_result__")


app = FastAPI(
    title="AutoKMS", version="0.1.0", openapi_url="/openapi.json", docs_url="/docs"
)
app.include_router(api.router)


@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {"status": "alive"}


@app.on_event("startup")
async def _startup():
    await api.initialize_async()
