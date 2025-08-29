import pytest
from autoapi.v3.bindings.rest import _build_router
from autoapi.v3.opspec import OpSpec
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, BulkCapable
from autoapi.v3.types import Column, String, App

pytestmark = pytest.mark.i9n


class Widget(Base, GUIDPk, BulkCapable):
    __tablename__ = "widgets_example_schemas"
    name = Column(String, nullable=False, info={"autoapi": {"examples": ["foo"]}})


def _openapi_for(ops):
    router = _build_router(Widget, [OpSpec(alias=a, target=t) for a, t in ops])
    app = App()
    app.include_router(router)
    return app.openapi()


def _resolve_schema(spec, schema):
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return spec["components"]["schemas"][ref]
    return schema


def test_create_request_model_examples():
    spec = _openapi_for([("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["examples"][0] == {"name": "foo"}
    assert schema["examples"][1] == [{"name": "foo"}]


def test_create_response_model_examples():
    spec = _openapi_for([("create", "create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    single, bulk = schema["examples"]
    assert single == {"name": "foo"}
    assert bulk == [{"name": "foo"}]


def test_bulk_request_model_examples():
    spec = _openapi_for([("bulk_create", "bulk_create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["examples"][0] == [{"name": "foo"}]


def test_bulk_response_model_examples():
    spec = _openapi_for([("bulk_create", "bulk_create")])
    path = f"/{Widget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    example = schema["examples"][0][0]
    assert example == {"name": "foo"}
