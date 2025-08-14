from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from autoapi.v2 import AutoAPI, Phase
from autoapi.v2.tables import Base

from .tables.key import Key
from .tables.key_version import KeyVersion


try:
    from swarmauri_secret_autogpg import AutoGpgSecretDrive
except Exception:
    AutoGpgSecretDrive = None

try:
    from swarmauri_crypto_paramiko import ParamikoCrypto
except Exception:
    ParamikoCrypto = None


def _secrets_driver_factory() -> Any:
    if AutoGpgSecretDrive is None:
        raise RuntimeError("AutoGpgSecretDrive not available")
    return AutoGpgSecretDrive()


def _crypto_plugin_factory() -> Any:
    if ParamikoCrypto is None:
        raise RuntimeError("ParamikoCrypto not available")
    return ParamikoCrypto()


# Build AutoAPI and mount on FastAPI app
api = AutoAPI(
    base=Base,
    include={Key, KeyVersion},
    prefix="/kms",
)


@api.register_hook(Phase.PRE_TX_BEGIN)
async def _stash_ctx(ctx):
    ctx["_kms_secrets"] = _secrets_driver_factory()
    ctx["_kms_crypto"] = _crypto_plugin_factory()


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
