from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, BulkCapable
from autoapi.v3.types import Column, String, App


class Widget(Base, GUIDPk, BulkCapable):
    __tablename__ = "widgets_bulk_schema"
    name = Column(String, nullable=False)


def _openapi_for(ops):
    router = _build_router(Widget, [OpSpec(alias=a, target=t) for a, t in ops])
    app = App()
    app.include_router(router)
    return app.openapi()


def test_create_request_schema_is_object():
    spec = _openapi_for([("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        schema = spec["components"]["schemas"][ref]
    assert schema.get("type") == "object"


def test_bulk_create_response_schema():
    spec = _openapi_for([("bulk_create", "bulk_create")])
    path = f"/{Widget.__name__.lower()}"
    ref = spec["paths"][path]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert ref.endswith("WidgetBulkCreateResponse")
    comp = spec["components"]["schemas"]["WidgetBulkCreateResponse"]
    assert comp["type"] == "array"
    items_ref = comp["items"]["$ref"]
    assert items_ref.endswith("WidgetRead")


def test_bulk_create_request_schema_has_item_ref():
    spec = _openapi_for([("bulk_create", "bulk_create")])
    path = f"/{Widget.__name__.lower()}"
    ref = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]["$ref"]
    assert ref.endswith("WidgetBulkCreateRequest")
    comp = spec["components"]["schemas"]["WidgetBulkCreateRequest"]
    items_ref = comp["items"]["$ref"]
    assert items_ref.endswith("WidgetCreate")


def test_create_and_bulk_create_handlers_and_schemas_bound():
    _ = _openapi_for(
        [
            ("create", "create"),
            ("bulk_create", "bulk_create"),
        ]
    )
    assert hasattr(Widget.schemas, "create")
    assert hasattr(Widget.schemas, "bulk_create")
    assert hasattr(Widget.handlers, "create")
    assert hasattr(Widget.handlers, "bulk_create")
    assert hasattr(Widget.handlers.create, "core")
    assert hasattr(Widget.handlers.bulk_create, "core")


def test_bulk_delete_response_schema():
    spec = _openapi_for([("bulk_delete", "bulk_delete")])
    path = f"/{Widget.__name__.lower()}"
    ref = spec["paths"][path]["delete"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert ref.endswith("WidgetBulkDeleteResponse")
    comp = spec["components"]["schemas"]["WidgetBulkDeleteResponse"]
    props = comp.get("properties", {})
    assert "deleted" in props
    assert props["deleted"]["type"] == "integer"
