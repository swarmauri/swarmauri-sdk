import asyncio

import pytest
from sqlalchemy import Column, Integer

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem


class Widget(TableBase):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True)


@pytest.mark.asyncio
async def test_initialize_schedules_task_for_sync_engine():
    app = TigrblApp(engine=mem(async_=False))
    app.tables["Widget"] = Widget

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True
