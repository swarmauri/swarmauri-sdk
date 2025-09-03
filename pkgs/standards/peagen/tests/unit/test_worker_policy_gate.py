import pytest
from types import SimpleNamespace
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from peagen.orm.workers import Worker
from autoapi.v3.orm.tables import Base
from peagen.defaults import DEFAULT_POOL_ID


@pytest.mark.asyncio
async def test_pre_create_policy_gate_allows_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        execution_options={"schema_translate_map": {"peagen": None}},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        ctx = {
            "env": SimpleNamespace(params={"pool_id": str(DEFAULT_POOL_ID)}),
            "request": SimpleNamespace(
                headers={}, client=SimpleNamespace(host="127.0.0.1")
            ),
            "db": session,
        }
        await Worker._pre_create_policy_gate(ctx)


@pytest.mark.asyncio
async def test_pre_update_policy_gate_allows_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        execution_options={"schema_translate_map": {"peagen": None}},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        ctx = {
            "env": SimpleNamespace(
                params={
                    "id": "00000000-0000-0000-0000-000000000000",
                    "pool_id": str(DEFAULT_POOL_ID),
                }
            ),
            "request": SimpleNamespace(
                headers={}, client=SimpleNamespace(host="127.0.0.1")
            ),
            "db": session,
        }
        await Worker._pre_update_policy_gate(ctx)
