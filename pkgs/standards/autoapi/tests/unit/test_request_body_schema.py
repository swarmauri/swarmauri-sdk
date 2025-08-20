from fastapi import FastAPI

from autoapi.v3.bindings import build_schemas
from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Integer, String
from autoapi.v3.specs import acol, IO, S


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_req_schema"
    name = acol(
        storage=S(type_=String, nullable=False),
        io=IO(in_verbs=("create", "update"), out_verbs=("read",)),
    )


def test_request_body_uses_schema_model():
    sp = OpSpec(alias="create", target="create")
    build_schemas(Widget, [sp])
    router = _build_router(Widget, [sp])
    app = FastAPI()
    app.include_router(router)
    spec = app.openapi()
    path = next(iter(spec["paths"]))

    request_schema = spec["paths"][path]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert request_schema["$ref"] == f"#/components/schemas/{Widget.__name__}Create"

    widget_schema = spec["components"]["schemas"][f"{Widget.__name__}Create"]
    assert "name" in widget_schema.get("properties", {})


def test_replace_request_body_excludes_pk():
    class Gadget(Base, GUIDPk):
        __tablename__ = "gadget_replace_schema"
        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read",)),
        )

    sp = OpSpec(alias="replace", target="replace")
    build_schemas(Gadget, [sp])
    router = _build_router(Gadget, [sp])
    app = FastAPI()
    app.include_router(router)
    spec = app.openapi()

    gadget_schema = spec["components"]["schemas"][f"{Gadget.__name__}Replace"]
    assert "id" not in gadget_schema.get("properties", {})
    assert "id" not in gadget_schema.get("required", [])


def test_delete_schema_pk_only_with_alias():
    Base.metadata.clear()

    class Thing(Base):
        __tablename__ = "thing_delete_schema"
        id = acol(
            storage=S(type_=Integer, primary_key=True),
            io=IO(alias_in="thing_id", out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create", "update"), out_verbs=("read",)),
        )

    sp = OpSpec(alias="delete", target="delete")
    build_schemas(Thing, [sp])
    schema = Thing.schemas.delete.in_
    assert list(schema.model_fields.keys()) == ["id"]
    assert schema.model_fields["id"].alias == "thing_id"


def test_clear_schema_has_no_input_model():
    Base.metadata.clear()

    class Clearable(Base):
        __tablename__ = "thing_clear_schema"
        id = acol(storage=S(type_=Integer, primary_key=True))

    sp = OpSpec(alias="clear", target="clear")
    build_schemas(Clearable, [sp])
    assert getattr(Clearable.schemas.clear, "in_", None) is None
