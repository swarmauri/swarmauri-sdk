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


def test_create_request_schema_allows_single_or_list():
    spec = _openapi_for([("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        schema = spec["components"]["schemas"][ref]
    union = schema.get("anyOf") or schema.get("oneOf")
    assert union is not None
    types = {item.get("type") or "object" for item in union}
    assert types == {"object", "array"}


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


def test_create_examples_prefer_bulk_list():
    spec = _openapi_for([("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    req_ref = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]["$ref"].split("/")[-1]
    req_schema = spec["components"]["schemas"][req_ref]
    req_examples = req_schema.get("examples")
    assert req_examples and isinstance(req_examples[0], list)

    resp_ref = spec["paths"][path]["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"]["$ref"].split("/")[-1]
    resp_schema = spec["components"]["schemas"][resp_ref]
    resp_examples = resp_schema.get("examples")
    assert resp_examples and isinstance(resp_examples[0], list)


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
