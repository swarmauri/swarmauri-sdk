from tigrbl.bindings.model import bind
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, Replaceable
from tigrbl.types import Column, String


class Gadget(Base, GUIDPk, Replaceable):
    __tablename__ = "gadgets_schemas_binding"
    name = Column(String, nullable=False)


def test_bind_generates_request_and_response_schemas():
    bind(Gadget)

    # create/update/replace/delete should have request and response schemas
    for alias in ("create", "update", "replace", "delete"):
        ns = getattr(Gadget.schemas, alias)
        assert getattr(ns, "in_", None) is not None
        assert getattr(ns, "out", None) is not None

    # list should expose request and response schemas
    list_ns = Gadget.schemas.list
    assert getattr(list_ns, "in_", None) is not None
    assert getattr(list_ns, "out", None) is not None
    assert not hasattr(list_ns, "list")

    # read should expose a response schema
    read_ns = Gadget.schemas.read
    assert getattr(read_ns, "out", None) is not None
