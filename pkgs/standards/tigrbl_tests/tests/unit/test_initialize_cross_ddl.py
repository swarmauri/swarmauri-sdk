import pytest

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import S
from tigrbl.shortcuts.column import acol
from tigrbl.shortcuts.engine import mem
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped


def _model():
    class Widget(TableBase):
        __tablename__ = "widgets"
        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        __tigrbl_cols__ = {"id": id}

    return Widget


@pytest.mark.asyncio
async def test_initialize_with_sync_engine():
    TableBase.metadata.clear()
    Widget = _model()
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    await app.initialize()
    assert getattr(app.tables, "Widget").name == "widgets"
