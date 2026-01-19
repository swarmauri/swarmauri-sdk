from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, BulkCapable, Mergeable
from tigrbl.specs import F, S, acol
from tigrbl.types import App, Mapped, String


class Widget(Base, GUIDPk, Mergeable):
    __tablename__ = "widgets_example_schemas"
    name: Mapped[str] = acol(
        storage=S(String, nullable=False), field=F(constraints={"examples": ["foo"]})
    )


class BulkWidget(Base, GUIDPk, BulkCapable, Mergeable):
    __tablename__ = "widgets_example_schemas_bulk"
    name: Mapped[str] = acol(
        storage=S(String, nullable=False), field=F(constraints={"examples": ["foo"]})
    )


def _openapi_for(model, ops):
    member_ops = {"read", "update", "replace", "merge", "delete"}
    specs = []
    for a, t in ops:
        arity = "member" if t in member_ops else "collection"
        specs.append(OpSpec(alias=a, target=t, arity=arity))
    router = _build_router(model, specs)
    app = App()
    app.include_router(router)
    return app.openapi()


def _resolve_schema(spec, schema):
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return spec["components"]["schemas"][ref]
    if "anyOf" in schema:
        return _resolve_schema(spec, schema["anyOf"][0])
    if "items" in schema:
        item = _resolve_schema(spec, schema["items"])
        schema["items"] = item
        if "examples" not in schema and "examples" in item:
            schema["examples"] = [item["examples"][0]]
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
    assert schema["items"]["properties"]["name"]["examples"][0] == "foo"


def test_bulk_response_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_create", "bulk_create")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    example = schema["examples"][0][0]
    assert example["name"] == "foo"


def test_merge_request_model_examples():
    spec = _openapi_for(Widget, [("merge", "merge")])
    path = f"/{Widget.__name__.lower()}/{{item_id}}"
    schema = spec["paths"][path]["patch"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["properties"]["name"]["examples"][0] == "foo"


def test_merge_response_model_examples():
    spec = _openapi_for(Widget, [("merge", "merge")])
    path = f"/{Widget.__name__.lower()}/{{item_id}}"
    schema = spec["paths"][path]["patch"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    assert schema["properties"]["name"]["examples"][0] == "foo"


def test_replace_request_model_examples():
    spec = _openapi_for(Widget, [("replace", "replace")])
    path = f"/{Widget.__name__.lower()}/{{item_id}}"
    schema = spec["paths"][path]["put"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["properties"]["name"]["examples"][0] == "foo"


def test_replace_response_model_examples():
    spec = _openapi_for(Widget, [("replace", "replace")])
    path = f"/{Widget.__name__.lower()}/{{item_id}}"
    schema = spec["paths"][path]["put"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    assert schema["properties"]["name"]["examples"][0] == "foo"


def test_bulk_update_request_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_update", "bulk_update")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["patch"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["items"]["properties"]["name"]["examples"][0] == "foo"


def test_bulk_update_response_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_update", "bulk_update")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["patch"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    example = schema["examples"][0][0]
    assert example["name"] == "foo"


def test_bulk_merge_request_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_merge", "bulk_merge")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["patch"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    schema = _resolve_schema(spec, schema)
    assert schema["items"]["properties"]["name"]["examples"][0] == "foo"


def test_bulk_merge_response_model_examples():
    spec = _openapi_for(BulkWidget, [("bulk_merge", "bulk_merge")])
    path = f"/{BulkWidget.__name__.lower()}"
    schema = spec["paths"][path]["patch"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    schema = _resolve_schema(spec, schema)
    example = schema["examples"][0][0]
    assert example["name"] == "foo"
