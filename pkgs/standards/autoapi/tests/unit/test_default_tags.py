from autoapi.v3.bindings.rest.router import _build_router
from autoapi.v3.ops import OpSpec
from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.types import Column, String


Base.metadata.clear()


class Widget(Base, GUIDPk):
    __tablename__ = "widgets"
    name = Column(String, nullable=False)


def test_router_default_tag():
    sp = OpSpec(alias="list", target="list")
    router = _build_router(Widget, [sp])
    route = router.routes[0]
    assert route.tags == [Widget.__name__]
