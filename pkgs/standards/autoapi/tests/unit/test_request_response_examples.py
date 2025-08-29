from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, BulkCapable
from autoapi.v3.types import Column, String, App


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_example_schemas"
    name = Column(String, nullable=False, info={"autoapi": {"examples": ["foo"]}})


class BulkWidget(Base, GUIDPk, BulkCapable):
    __tablename__ = "widgets_example_schemas_bulk"
    name = Column(String, nullable=False, info={"autoapi": {"examples": ["foo"]}})


def _openapi_for(model, ops):
    router = _build_router(model, [OpSpec(alias=a, target=t) for a, t in ops])
    app = App()
    app.include_router(router)
    return app.openapi()


def _resolve_schema(spec, schema):
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return spec["components"]["schemas"][ref]
    return schema


def test_create_request_model_examples():
    spec = _openapi_for(Widget, [("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["properties"]["name"]["examples"][0] == "foo"


def test_create_response_model_examples():
    spec = _openapi_for(Widget, [("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    assert schema["properties"]["name"]["examples"][0] == "foo"


def test_bulk_request_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_create", "bulk_create")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["examples"][0] == [{"name": "foo"}]


def test_bulk_response_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_create", "bulk_create")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    example = schema["examples"][0][0]
    assert example == {"name": "foo"}
