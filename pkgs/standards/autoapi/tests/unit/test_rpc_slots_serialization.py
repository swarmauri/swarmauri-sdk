from fastapi.testclient import TestClient
from sqlalchemy import Column, String
from autoapi.v3 import AutoApp, op_ctx
from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk


class SlotsObj:
    __slots__ = ("x",)

    def __init__(self, x: int) -> None:
        self.x = x


Base.metadata.clear()


class Widget(Base, GUIDPk):
    __tablename__ = "widgets"
    name = Column(String, nullable=False)

    @op_ctx(alias="slot", target="custom")
    def slot(cls, ctx):
        return SlotsObj(5)


def test_rpc_serializes_slots_objects():
    app = AutoApp()
    app.include_model(Widget)
    app.mount_jsonrpc()
    client = TestClient(app)
    resp = client.post(
        "/rpc", json={"jsonrpc": "2.0", "method": "Widget.slot", "id": 1}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == {"x": 5}
