from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


Base.metadata.clear()


class Widget(Base, GUIDPk):
    __tablename__ = "widgets"
    name = Column(String, nullable=False)


def test_router_default_tag():
    sp = OpSpec(alias="list", target="list")
    router = _build_router(Widget, [sp])
    route = router.routes[0]
    assert route.tags == [Widget.__name__]
