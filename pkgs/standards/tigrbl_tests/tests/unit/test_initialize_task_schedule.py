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
<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    app.models["Widget"] = Widget

    result = app.initialize()
=======
    router = TigrblApp(engine=mem(async_=False))
    router.models["Widget"] = Widget

    result = router.initialize()
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c

    assert isinstance(result, asyncio.Task)

    await result

<<<<<<< HEAD
    assert getattr(app, "_ddl_executed", False) is True
=======
    assert getattr(router, "_ddl_executed", False) is True
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
