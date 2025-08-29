from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.bindings.rest import _build_router
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_security"
    __autoapi_auth_dep__ = staticmethod(lambda cred=Security(HTTPBearer()): cred)
    __autoapi_allow_anon__ = ["list"]


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
