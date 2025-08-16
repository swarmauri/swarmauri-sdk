from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Column, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets"
    name = Column(String, nullable=False)


def test_router_default_tag():
    sp = OpSpec(alias="list", target="list")
    router = _build_router(Widget, [sp])
    route = router.routes[0]
    assert route.tags == ["widgets"]
