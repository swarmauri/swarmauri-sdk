from fastapi import FastAPI

from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Column, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_no_body"
    name = Column(String, nullable=False)


def test_read_has_no_request_body():
    sp = OpSpec(alias="read", target="read")
    router = _build_router(Widget, [sp])
    app = FastAPI()
    app.include_router(router)
    spec = app.openapi()
    read_spec = spec["paths"]["/widgets_no_body/{item_id}"]["get"]
    assert "requestBody" not in read_spec
    params = read_spec.get("parameters", [])
    assert any(p["name"] == "item_id" and p["in"] == "path" for p in params)
