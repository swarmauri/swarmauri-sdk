from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, BulkCapable, Replaceable
from tigrbl.types import Column, String, App


class Widget(Base, GUIDPk, BulkCapable, Replaceable):
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
    # The create handler for bulk-capable tables accepts either a single object
    # or an array of objects. Inspect the first variant to ensure it is an
    # object schema.
    if "anyOf" in schema:
        schema = schema["anyOf"][0]
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
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    assert schema["type"] == "array"
    items_ref = schema["items"]["$ref"]
    assert items_ref.endswith("WidgetBulkCreateItem")


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


def test_bulk_update_request_and_response_schemas():
    spec = _openapi_for([("bulk_update", "bulk_update")])
    path = f"/{Widget.__name__.lower()}"
    # request schema
    req_schema = spec["paths"][path]["patch"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert req_schema["type"] == "array"
    assert req_schema["items"]["$ref"].endswith("WidgetBulkUpdateItem")
    # response schema
    resp_ref = spec["paths"][path]["patch"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert resp_ref.endswith("WidgetBulkUpdateResponse")
    resp_comp = spec["components"]["schemas"]["WidgetBulkUpdateResponse"]
    assert resp_comp["items"]["$ref"].endswith("WidgetRead")
    assert "WidgetRead" in spec["components"]["schemas"]


def test_bulk_replace_request_and_response_schemas():
    spec = _openapi_for([("bulk_replace", "bulk_replace")])
    path = f"/{Widget.__name__.lower()}"
    # request schema
    req_schema = spec["paths"][path]["put"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert req_schema["type"] == "array"
    assert req_schema["items"]["$ref"].endswith("WidgetBulkReplaceItem")
    # response schema
    resp_ref = spec["paths"][path]["put"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert resp_ref.endswith("WidgetBulkReplaceResponse")
    resp_comp = spec["components"]["schemas"]["WidgetBulkReplaceResponse"]
    assert resp_comp["items"]["$ref"].endswith("WidgetRead")


def test_bulk_merge_request_and_response_schemas():
    spec = _openapi_for([("bulk_merge", "bulk_merge")])
    path = f"/{Widget.__name__.lower()}"
    # request schema
    req_schema = spec["paths"][path]["patch"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert req_schema["type"] == "array"
    assert req_schema["items"]["type"] == "object"
    # bulk merge currently returns no content in the response
    assert "content" not in spec["paths"][path]["patch"]["responses"]["200"]


def test_update_and_bulk_update_schema_names_do_not_collide():
    spec = _openapi_for([("update", "update"), ("bulk_update", "bulk_update")])
    base = f"/{Widget.__name__.lower()}"
    update_path = f"{base}/{{item_id}}"
    # single update schema
    upd_ref = spec["paths"][update_path]["patch"]["requestBody"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert upd_ref.endswith("WidgetUpdateRequest")
    # bulk update schema
    bulk_schema = spec["paths"][base]["patch"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert bulk_schema["type"] == "array"
    assert bulk_schema["items"]["$ref"].endswith("WidgetBulkUpdateItem")
