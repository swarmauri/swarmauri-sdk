from __future__ import annotations

from sqlalchemy import Column, String
from tigrbl import TableBase, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.shortcuts.engine import mem


class TransportWidget(TableBase, GUIDPk):
    __tablename__ = "transport_widgets"
    __resource__ = "transport-widget"
    name = Column(String, nullable=False)


app = TigrblApp(engine=mem(async_=False))
app.include_tables([TransportWidget])
app.install_engines(tables=tuple(app.tables.values()))
app.mount_jsonrpc()
app.initialize()
