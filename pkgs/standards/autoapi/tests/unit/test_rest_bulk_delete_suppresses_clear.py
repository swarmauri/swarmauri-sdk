from autoapi.v3.bindings.rest import build_router_and_attach
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.ops import OpSpec
from autoapi.v3.orm.tables import Base
from autoapi.v3.types import Column, String


def test_bulk_delete_suppresses_clear_route():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items_bulk_delete_route"
        name = Column(String, nullable=False)

    build_router_and_attach(
        Item,
        [
            OpSpec(alias="clear", target="clear"),
            OpSpec(alias="bulk_delete", target="bulk_delete"),
        ],
    )

    aliases = {route.name.split(".", 1)[1] for route in Item.rest.router.routes}
    assert "bulk_delete" in aliases
    assert "clear" not in aliases
