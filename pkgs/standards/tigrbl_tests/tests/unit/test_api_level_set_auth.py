from tigrbl import TigrblApp
from tigrbl.security import HTTPBearer
from tigrbl.types import Router, Security
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_api_level_set_auth"
    __tigrbl_allow_anon__ = ["list"]


def test_api_level_auth_dep_applied_per_route():
    router = Router()
    app = TigrblApp()
    app.set_auth(authn=lambda cred=Security(HTTPBearer()): cred, allow_anon=False)
    app.include_models([Widget])
    router.include_router(app.router)
    schema = router.openapi()
    paths = {route.name: route.path_template for route in app.routers["Widget"].routes}
    list_sec = schema["paths"][paths["Widget.list"]]["get"].get("security")
    read_sec = schema["paths"][paths["Widget.read"]]["get"].get("security")
    assert not list_sec
    assert read_sec == [{"HTTPBearer": []}]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
