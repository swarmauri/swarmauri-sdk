from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer

from tigrbl import TigrblApp, TigrblRouter
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.table import Base


class SimpleApp(TigrblApp):
    TITLE = "TestApp"
    VERSION = "0.0"
    LIFESPAN = None
    ROUTERS: tuple = ()
    MODELS: tuple = ()
    MIDDLEWARES: tuple = ()


class SimpleRouter(TigrblRouter):
    PREFIX = ""
    TAGS: list[str] = []


def test_base_app_supports_initialize():
    class Widget(Base):
        __tablename__ = "widgets"

        id = Column(Integer, primary_key=True)

    app = SimpleApp(engine=mem(async_=False))
    app.tables["Widget"] = Widget.__table__

    try:
        app.initialize()
    finally:
        _resolver.set_default(None)

    assert getattr(app, "_ddl_executed", False) is True
    tables = getattr(app, "tables", None)
    assert tables is not None
    assert tables["Widget"] is Widget.__table__


def test_base_router_supports_initialize_sync():
    class Widget(Base):
        __tablename__ = "widgets_sync"

        id = Column(Integer, primary_key=True)

    router = SimpleRouter(engine=mem(async_=False))
    router.tables["Widget"] = Widget.__table__

    router.initialize()

    assert getattr(router, "_ddl_executed", False) is True
    assert router.tables["Widget"] is Widget.__table__


@pytest.mark.asyncio
async def test_base_router_supports_initialize_async():
    class Gadget(Base):
        __tablename__ = "gadgets"

        id = Column(Integer, primary_key=True)

    router = SimpleRouter(engine=mem())
    router.tables["Gadget"] = Gadget.__table__

    await router.initialize()

    assert getattr(router, "_ddl_executed", False) is True
    assert router.tables["Gadget"] is Gadget.__table__
