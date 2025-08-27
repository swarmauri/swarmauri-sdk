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
    assert request_schema["$ref"] == "#/components/schemas/WidgetCreate"

    widget_schema = spec["components"]["schemas"]["WidgetCreate"]
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

    gadget_schema = spec["components"]["schemas"]["GadgetReplace"]
    assert "id" not in gadget_schema.get("properties", {})
    assert "id" not in gadget_schema.get("required", [])
