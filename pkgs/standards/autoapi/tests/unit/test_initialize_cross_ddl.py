import pytest
from autoapi.v3.autoapp import AutoApp
from autoapi.v3 import Base
from autoapi.v3.specs import S, acol
from autoapi.v3.engine.shortcuts import mem
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped


def _model():
    class Widget(Base):
        __tablename__ = "widgets"
        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        __autoapi_cols__ = {"id": id}

    return Widget


@pytest.mark.asyncio
async def test_initialize_with_sync_engine():
    Base.metadata.clear()
    Widget = _model()
    api = AutoApp(engine=mem(async_=False))
    api.include_model(Widget)
    await api.initialize()
    assert getattr(api.tables, "Widget").name == "widgets"
