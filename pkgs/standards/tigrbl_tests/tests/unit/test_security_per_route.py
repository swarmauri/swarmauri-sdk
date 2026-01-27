from tigrbl.op import OpSpec
from tigrbl import TigrblApp
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.bindings.rest.router import _build_router
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_security"
    __tigrbl_auth_dep__ = staticmethod(lambda cred=Security(HTTPBearer()): cred)
    __tigrbl_allow_anon__ = ["list"]


def test_security_applied_per_route():
    router = _build_router(
        Widget,
        [OpSpec(alias="list", target="list"), OpSpec(alias="read", target="read")],
    )
    app = FastAPI()
    app.include_router(router)
    schema = app.openapi()
    paths = {route.name: route.path for route in router.routes}
    list_sec = schema["paths"][paths["Widget.list"]]["get"].get("security")
    read_sec = schema["paths"][paths["Widget.read"]]["get"].get("security")
    assert not list_sec
    assert read_sec == [{"HTTPBearer": []}]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]


def test_set_auth_after_include_model_applies_security():
    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_security"

    api = TigrblApp()
    api.include_model(Gadget)
    api.set_auth(authn=lambda cred=Security(HTTPBearer()): cred, allow_anon=False)
    app = FastAPI()
    app.include_router(api.router)
    spec = app.openapi()
    post_sec = spec["paths"]["/gadget"]["post"].get("security")
    assert post_sec == [{"HTTPBearer": []}]
