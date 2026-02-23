import asyncio

import pytest
from sqlalchemy import Column, Integer

from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem


class AsyncWidget(Base):
    __tablename__ = "widgets_async_router"

    id = Column(Integer, primary_key=True)


class SyncWidget(Base):
    __tablename__ = "widgets_sync_router"

    id = Column(Integer, primary_key=True)


@pytest.mark.asyncio
async def test_initialize_handles_mixed_sync_async_routers():
    routers = [TigrblRouter(engine=mem()), TigrblRouter(engine=mem(async_=False))]
    router = routers[0]
    router.include_table(AsyncWidget, prefix="")
    routers[1].include_table(SyncWidget, prefix="")

    app = TigrblApp(engine=mem(async_=False))
    app.include_routers(routers)

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True
    assert getattr(router, "_ddl_executed", False) is True
    assert getattr(routers[1], "_ddl_executed", False) is True
