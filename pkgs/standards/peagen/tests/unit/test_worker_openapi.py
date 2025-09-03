from autoapi.v3 import get_schema
from peagen.orm import Worker


def test_worker_create_schema_includes_fields():
    schema = get_schema(Worker, op="create", kind="in")
    assert "url" in schema.model_fields
    assert "pool_id" in schema.model_fields


def test_worker_openapi_includes_request_fields():
    from peagen.gateway import app

    spec = app.openapi()
    props = spec["components"]["schemas"]["WorkerCreateRequest"]["properties"]
    assert "url" in props
    assert "pool_id" in props
