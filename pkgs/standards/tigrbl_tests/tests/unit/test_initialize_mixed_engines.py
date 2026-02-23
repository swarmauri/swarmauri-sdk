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
    app = TigrblApp(engine=mem(async_=False))

    router = TigrblRouter(engine=mem())
    router.include_table(AsyncWidget, prefix="")
    app.include_router(router)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(SyncWidget, prefix="")
    app.include_router(router)

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True
