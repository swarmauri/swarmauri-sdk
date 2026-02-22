import pytest
from tigrbl import TigrblApp
from tigrbl import Base
from tigrbl.specs import S, acol
from tigrbl.engine.shortcuts import mem
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped


def _model():
    class Widget(Base):
        __tablename__ = "widgets"
        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        __tigrbl_cols__ = {"id": id}

    return Widget


@pytest.mark.asyncio
async def test_initialize_with_sync_engine():
    Base.metadata.clear()
    Widget = _model()
    router = TigrblApp(engine=mem(async_=False))
    router.include_model(Widget)
    await router.initialize()
    assert getattr(router.tables, "Widget").name == "widgets"
