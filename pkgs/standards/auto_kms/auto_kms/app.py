from __future__ import annotations

from autoapi.v3 import AutoApp
from .orm import Key, KeyVersion

from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_standard.key_providers import InMemoryKeyProvider

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


# API-level hooks (v3): stash shared services into ctx before any handler runs
async def _stash_ctx(ctx):
    global CRYPTO, KEY_PROVIDER
    try:
        CRYPTO
    except NameError:
        CRYPTO = ParamikoCrypto()
    try:
        KEY_PROVIDER
    except NameError:
        KEY_PROVIDER = InMemoryKeyProvider()
    ctx["crypto"] = CRYPTO
    ctx["key_provider"] = KEY_PROVIDER


app = AutoApp(
    title="AutoKMS",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    get_async_db=get_async_db,
    api_hooks={"*": {"PRE_TX_BEGIN": [_stash_ctx]}},
)


# Custom ops return raw dicts so no finalize hook needed
app.include_models([Key, KeyVersion], base_prefix="/kms")
app.mount_jsonrpc(prefix="/kms/rpc")
app.attach_diagnostics(prefix="/system")


# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    await app.initialize_async()
