import asyncio

import pytest
from sqlalchemy import Column, Integer

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True)


@pytest.mark.asyncio
async def test_initialize_schedules_task_for_sync_engine():
    router = TigrblApp(engine=mem(async_=False))
    router.models["Widget"] = Widget

    result = router.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(router, "_ddl_executed", False) is True
