import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from peagen.models import Base, AbuseRecord
from peagen.gateway.db_helpers import (
    record_unknown_handler,
    fetch_banned_ips,
    mark_ip_banned,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_unknown_handler_ban_cycle(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with SessionLocal() as session:
        count = await record_unknown_handler(session, "1.2.3.4")
        assert count == 1

    async with SessionLocal() as session:
        count = await record_unknown_handler(session, "1.2.3.4")
        assert count == 2
        record = await session.get(AbuseRecord, "1.2.3.4")
        assert record and record.count == 2
        assert record.first_seen is not None

    async with SessionLocal() as session:
        await mark_ip_banned(session, "1.2.3.4")

    async with SessionLocal() as session:
        banned = await fetch_banned_ips(session)
        assert "1.2.3.4" in banned
