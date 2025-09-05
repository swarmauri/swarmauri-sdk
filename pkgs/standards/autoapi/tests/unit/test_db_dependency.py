from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.op import OpSpec
from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.types import Column, String


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
