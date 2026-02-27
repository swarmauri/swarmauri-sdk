import pytest

from tigrbl import Base, TigrblApp
from tigrbl.specs import S, acol
from tigrbl.shortcuts.engine import mem
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
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    await app.initialize()
    assert getattr(app.tables, "Widget").name == "widgets"
