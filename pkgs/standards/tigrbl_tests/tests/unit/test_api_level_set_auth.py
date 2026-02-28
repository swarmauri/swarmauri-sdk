import pytest

from tigrbl import TigrblApp
from tigrbl import Router
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl import HTTPBearer
from tigrbl.security import Security


pytestmark = pytest.mark.xfail(
    reason="Router does not support include_router(...)",
    strict=False,
)


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_router_level_set_auth"
    __tigrbl_allow_anon__ = ["list"]


def test_router_level_auth_dep_applied_per_route():
    router = Router()
    app = TigrblApp()
    app.set_auth(authn=lambda cred=Security(HTTPBearer()): cred, allow_anon=False)
    app.include_tables([Widget])
    router.include_router(app.router)
    schema = router.openapi()
    paths = {route.name: route.path_template for route in app.routers["Widget"].routes}
    list_sec = schema["paths"][paths["Widget.list"]]["get"].get("security")
    read_sec = schema["paths"][paths["Widget.read"]]["get"].get("security")
    assert not list_sec
    assert read_sec == [{"HTTPBearer": []}]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
