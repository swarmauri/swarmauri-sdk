import asyncio

import pytest
from sqlalchemy import Column, Integer

from tigrbl import Base, TigrblApi, TigrblApp
from tigrbl.engine.shortcuts import mem


class AsyncWidget(Base):
    __tablename__ = "widgets_async_api"

    id = Column(Integer, primary_key=True)


class SyncWidget(Base):
    __tablename__ = "widgets_sync_api"

    id = Column(Integer, primary_key=True)


@pytest.mark.asyncio
async def test_initialize_handles_mixed_sync_async_apis():
    async_api = TigrblApi(engine=mem())
    async_api.include_model(AsyncWidget, prefix="")

    sync_api = TigrblApi(engine=mem(async_=False))
    sync_api.include_model(SyncWidget, prefix="")

    app = TigrblApp(engine=mem(async_=False))
    app.include_apis([async_api, sync_api])

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True
    assert getattr(async_api, "_ddl_executed", False) is True
    assert getattr(sync_api, "_ddl_executed", False) is True
