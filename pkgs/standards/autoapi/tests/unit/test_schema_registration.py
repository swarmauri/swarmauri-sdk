from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Column, String


def test_all_ops_have_in_and_out_schemas():
    class Widget(Base, GUIDPk):
        __tablename__ = "schema_widgets"
        name = Column(String, nullable=False)

    api = AutoAPI()
    api.include_model(Widget)

    read_ns = Widget.schemas.read
    assert read_ns.in_ is not None
    assert read_ns.out is not None

    list_ns = Widget.schemas.list
    assert list_ns.in_ is not None
    assert list_ns.out is not None
