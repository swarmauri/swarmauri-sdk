import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tigrbl.runtime.executor import _in_tx


@pytest.mark.asyncio
async def test_in_tx_detects_async_session_transaction():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with SessionLocal() as session:
        assert _in_tx(session) is False
        await session.begin()
        assert _in_tx(session) is True
