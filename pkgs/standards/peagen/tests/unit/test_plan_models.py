
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from peagen.models.plan import DOEPlan, Base


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plan_create_and_lock(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/db.sqlite")
    Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as s:
        plan = DOEPlan(name="test", description="desc", data={"a": 1})
        s.add(plan)
        await s.commit()
        pid = plan.id

    async with Session() as s:
        plan = await s.get(DOEPlan, pid)
        assert plan.locked is False
        plan.locked = True
        await s.commit()

    async with Session() as s:
        plan = await s.get(DOEPlan, pid)
        assert plan.locked is True

