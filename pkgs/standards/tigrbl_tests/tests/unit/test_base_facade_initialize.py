from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer

from tigrbl.app._app import App as _App
from tigrbl.api._api import Api as _Api
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.table import Base


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True)


class SimpleApp(_App):
    TITLE = "TestApp"
    VERSION = "0.0"
    LIFESPAN = None
    APIS: tuple = ()
    MODELS: tuple = ()
    MIDDLEWARES: tuple = ()


class SimpleApi(_Api):
    PREFIX = ""
    TAGS: list[str] = []


def test_base_app_supports_initialize():
    app = SimpleApp(engine=mem(async_=False))
    app.models["Widget"] = Widget

    try:
        app.initialize()
    finally:
        _resolver.set_default(None)

    assert getattr(app, "_ddl_executed", False) is True
    tables = getattr(app, "tables", None)
    assert tables is not None
    assert getattr(tables, "Widget", None) is Widget.__table__


def test_base_api_supports_initialize_sync():
    api = SimpleApi(engine=mem(async_=False))
    api.models["Widget"] = Widget

    api.initialize()

    assert getattr(api, "_ddl_executed", False) is True
    assert api.tables["Widget"] is Widget.__table__


@pytest.mark.asyncio
async def test_base_api_supports_initialize_async():
    class Gadget(Base):
        __tablename__ = "gadgets"

        id = Column(Integer, primary_key=True)

    api = SimpleApi(engine=mem())
    api.models["Gadget"] = Gadget

    await api.initialize()

    assert getattr(api, "_ddl_executed", False) is True
    assert api.tables["Gadget"] is Gadget.__table__
