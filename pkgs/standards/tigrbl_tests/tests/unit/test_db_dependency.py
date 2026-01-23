from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_db_dep"
    name = Column(String, nullable=False)


def test_db_injected_via_dependency():
    sp = OpSpec(alias="list", target="list")
    router = _build_router(Widget, [sp])
    route = router.routes[0]
    assert "db" not in {p.name for p in route.dependant.path_params}
    assert "db" not in {p.name for p in route.dependant.query_params}
    assert any(d.name == "db" for d in route.dependant.dependencies)
