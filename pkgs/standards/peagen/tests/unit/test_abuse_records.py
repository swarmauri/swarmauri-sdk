import datetime as dt

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from peagen.orm import Base, AbuseRecord
from peagen.gateway.db_helpers import (
    record_unknown_handler,
    fetch_banned_ips,
    mark_ip_banned,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_and_ban_ip(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/test.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with Session() as session:
        count = await record_unknown_handler(session, "1.2.3.4")
        assert count == 1

    async with Session() as session:
        count = await record_unknown_handler(session, "1.2.3.4")
        assert count == 2
        rec = await session.get(AbuseRecord, "1.2.3.4")
        assert rec.count == 2
        assert isinstance(rec.first_seen, dt.datetime)
        assert rec.banned is False

    async with Session() as session:
        await mark_ip_banned(session, "1.2.3.4")
        banned = await fetch_banned_ips(session)
        assert "1.2.3.4" in banned
        rec = await session.get(AbuseRecord, "1.2.3.4")
        assert rec.banned is True

    await engine.dispose()
