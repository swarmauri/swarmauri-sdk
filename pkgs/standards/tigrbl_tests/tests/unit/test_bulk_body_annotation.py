from typing import get_args, get_origin

from tigrbl.bindings.rest.collection import _make_collection_endpoint
from tigrbl.orm.mixins import BulkCapable, GUIDPk
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.types import Column, String


def test_bulk_create_body_annotation_is_list() -> None:
    Base.metadata.clear()

    class Widget(Base, GUIDPk, BulkCapable):
        __tablename__ = "widgets_anno"
        name = Column(String, nullable=False)

    sp = OpSpec(alias="bulk_create", target="bulk_create")
    endpoint = _make_collection_endpoint(
        Widget, sp, resource="widget", db_dep=lambda: None
    )
    body_ann = endpoint.__annotations__["body"]
    assert get_origin(body_ann) is list
    assert get_args(body_ann)[0] is getattr(Widget.schemas.bulk_create, "in_item")
