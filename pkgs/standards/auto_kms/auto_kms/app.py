from __future__ import annotations

from fastapi import FastAPI
from autoapi.v3 import AutoAPI

from .tables.key import Key
from .tables.key_version import KeyVersion

from swarmauri_secret_autogpg import AutoGpgSecretDrive
from swarmauri_crypto_paramiko import ParamikoCrypto

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DB_URL = os.getenv("KMS_DATABASE_URL", "sqlite+aiosqlite:///./kms.db")

engine = create_async_engine(DB_URL, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_db():
    async with AsyncSessionLocal() as s:
        try:
            yield s
        finally:
            await s.close()


app = FastAPI(
    title="AutoKMS", version="0.1.0", openapi_url="/openapi.json", docs_url="/docs"
)

# API-level hooks (v3): stash shared services into ctx before any handler runs
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


# Construct AutoAPI with api-level hooks; custom ops return raw dicts so no finalize hook needed
api = AutoAPI(
    app=app, get_async_db=get_async_db, api_hooks={"*": {"PRE_TX_BEGIN": [_stash_ctx]}}
)
api.include_models([Key, KeyVersion], base_prefix="/kms")
api.mount_jsonrpc(prefix="/kms/rpc")
api.attach_diagnostics(prefix="/system")
