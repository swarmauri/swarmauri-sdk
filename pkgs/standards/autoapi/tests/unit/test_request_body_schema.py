from autoapi.v3.types import App

from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Column, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_req_schema"
    name = Column(String, nullable=False)


def test_request_body_uses_schema_model():
    sp = OpSpec(alias="create", target="create")
    router = _build_router(Widget, [sp])
    app = App()
    app.include_router(router)
    spec = app.openapi()
    path = f"/{Widget.__name__.lower()}"
    request_schema = spec["paths"][path]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    if "$ref" in request_schema:
        ref = request_schema["$ref"].split("/")[-1]
        request_schema = spec["components"]["schemas"][ref]
    elif "anyOf" in request_schema:
        first = request_schema["anyOf"][0]
        if "$ref" in first:
            ref = first["$ref"].split("/")[-1]
            request_schema = spec["components"]["schemas"][ref]
        else:
            request_schema = first
    assert request_schema.get("type") == "object"

    widget_schema = spec["components"]["schemas"]["WidgetCreateRequest"]
    assert "name" in widget_schema.get("properties", {})


def test_replace_request_body_excludes_pk():
    class Gadget(Base, GUIDPk):
        __tablename__ = "gadget_replace_schema"
        name = Column(String, nullable=False)

    sp = OpSpec(alias="replace", target="replace")
    router = _build_router(Gadget, [sp])
    app = App()
    app.include_router(router)
    spec = app.openapi()

    gadget_schema = spec["components"]["schemas"]["GadgetReplaceRequest"]
    assert "id" not in gadget_schema.get("properties", {})
    assert "id" not in gadget_schema.get("required", [])
