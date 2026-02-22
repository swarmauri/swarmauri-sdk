from tigrbl import TigrblApp
from tigrbl.security import HTTPBearer
from tigrbl.types import APIRouter, Security
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.bindings.rest.router import _build_router


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_security"


def _auth_dep(cred=Security(HTTPBearer())):
    return cred


def test_security_metadata_applied_per_route_from_opspec_secdeps():
    router = _build_router(
        Widget,
        [
            OpSpec(alias="list", target="list"),
            OpSpec(alias="read", target="read", secdeps=(_auth_dep,)),
        ],
    )
    app = APIRouter()
    app.include_router(router)
    schema = app.openapi()
    paths = {route.name: route.path_template for route in router.routes}
    list_sec = schema["paths"][paths["Widget.list"]]["get"].get("security")
    read_sec = schema["paths"][paths["Widget.read"]]["get"].get("security")
    assert not list_sec
    assert read_sec == [{"HTTPBearer": []}]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]


def test_set_auth_after_include_model_exposes_security_metadata_only():
    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_security"

    router = TigrblApp()
    router.include_model(Gadget)

    def authn(cred=Security(HTTPBearer())):
        return cred

    router.set_auth(authn=authn, allow_anon=False)
    app = APIRouter()
    app.include_router(router.router)
    spec = app.openapi()
    post_sec = spec["paths"]["/gadget"]["post"].get("security")
    assert post_sec == [{"HTTPBearer": []}]
