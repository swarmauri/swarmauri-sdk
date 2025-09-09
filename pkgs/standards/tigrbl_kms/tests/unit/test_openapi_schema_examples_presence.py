import importlib
import warnings

MODELS = {
    "Key": "/kms/key",
    "KeyVersion": "/kms/key_version",
}


def _resolve(schema, spec):
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return spec["components"]["schemas"][ref]
    return schema


def _get_app_and_spec():
    app_module = importlib.reload(importlib.import_module("tigrbl_kms.app"))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        spec = app_module.app.openapi()
    return app_module.app, spec


def test_request_and_response_body_examples_present():
    """Ensure each ORM exposes request and response bodies with examples."""
    _, spec = _get_app_and_spec()
    for path in MODELS.values():
        op = spec["paths"][path]["post"]
        req_schema = _resolve(
            op["requestBody"]["content"]["application/json"]["schema"], spec
        )
        res_schema = _resolve(
            op["responses"]["200"]["content"]["application/json"]["schema"], spec
        )
        assert req_schema is not None
        assert "examples" in res_schema


def test_all_schemas_listed_in_openapi():
    """Validate that all dynamically generated schemas appear in OpenAPI."""
    app, spec = _get_app_and_spec()
    component_names = set(spec["components"]["schemas"])
    standard_ops = ["create", "read", "update", "replace", "delete", "list"]
    for model_name in MODELS:
        model_ns = getattr(app.schemas, model_name)
        for alias in standard_ops:
            if not hasattr(model_ns, alias):
                continue
            op_ns = getattr(model_ns, alias)
            if alias in {"create", "update", "replace"} and hasattr(op_ns, "in_"):
                assert op_ns.in_.__name__ in component_names
            if hasattr(op_ns, "out"):
                assert op_ns.out.__name__ in component_names


def test_app_rest_and_tables_house_all_models():
    """Confirm app containers expose schemas for all models."""
    app, _ = _get_app_and_spec()
    schema_models = {name for name in dir(app.schemas) if not name.startswith("_")}
    rest_models = {name for name in dir(app.rest) if not name.startswith("_")}
    table_models = set(app.tables.keys())
    assert schema_models == rest_models == table_models == set(MODELS.keys())
