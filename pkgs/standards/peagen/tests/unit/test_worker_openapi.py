from autoapi.v3 import AutoApp, get_schema
from peagen.orm import Worker
from peagen.gateway.db import ENGINE


def test_worker_create_schema_includes_fields():
    schema = get_schema(Worker, op="create", kind="in")
    assert "url" in schema.model_fields
    assert "pool_id" in schema.model_fields


def test_worker_openapi_includes_request_fields():
    """Ensure the generated OpenAPI spec exposes required Worker fields."""

    app = AutoApp(title="Test Gateway", engine=ENGINE)
    app.include_models([Worker])

    spec = app.openapi()
    props = spec["components"]["schemas"]["WorkerCreateRequest"]["properties"]
    assert "url" in props
    assert "pool_id" in props
