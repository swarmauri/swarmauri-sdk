from tigrbl import TigrblApp
from tigrbl.security import HTTPBearer
from tigrbl.types import APIRouter, Security
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_api_level_set_auth"
    __tigrbl_allow_anon__ = ["list"]


def test_api_level_auth_dep_applied_as_openapi_metadata_only():
    app = APIRouter()
    api = TigrblApp()

    def authn(cred=Security(HTTPBearer())):
        return cred

    api.set_auth(authn=authn, allow_anon=False)
    api.include_models([Widget])
    app.include_router(api.router)
    schema = app.openapi()
    paths = {route.name: route.path_template for route in api.routers["Widget"].routes}
    list_sec = schema["paths"][paths["Widget.list"]]["get"].get("security")
    read_sec = schema["paths"][paths["Widget.read"]]["get"].get("security")
    assert not list_sec
    assert read_sec == [{"HTTPBearer": []}]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
