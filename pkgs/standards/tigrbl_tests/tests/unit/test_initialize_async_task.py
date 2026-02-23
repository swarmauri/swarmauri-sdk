import asyncio

import pytest
from sqlalchemy import Column, Integer

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem


class Widget(Base):
    __tablename__ = "widgets_async_task"

    id = Column(Integer, primary_key=True)


@pytest.mark.asyncio
async def test_initialize_returns_task_for_async_engine():
    app = TigrblApp(engine=mem())
    app.include_model(Widget, prefix="")

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True
