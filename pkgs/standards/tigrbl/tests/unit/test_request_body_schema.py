from tigrbl.types import App

from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


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
        ref = next(
            (s["$ref"].split("/")[-1] for s in request_schema["anyOf"] if "$ref" in s),
            None,
        )
        if ref is not None:
            request_schema = spec["components"]["schemas"][ref]
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
