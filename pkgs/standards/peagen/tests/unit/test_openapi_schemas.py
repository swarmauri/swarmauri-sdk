import os

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from peagen.gateway import app  # noqa: E402

spec = app.openapi()


def test_request_and_response_schemas_present():
    schemas = spec["components"]["schemas"]
    for name in app.models:
        assert f"{name}CreateRequest" in schemas
        assert f"{name}CreateResponse" in schemas
        clear_schema = schemas.get(f"{name}ClearResponse")
        assert clear_schema is not None
        assert "examples" in clear_schema and clear_schema["examples"]


def test_all_expected_schemas_present_in_openapi():
    schemas = spec["components"]["schemas"]
    expected_suffixes = [
        "CreateRequest",
        "CreateResponse",
        "ReadResponse",
        "ListResponse",
        "UpdateRequest",
        "UpdateResponse",
        "ReplaceRequest",
        "ReplaceResponse",
        "DeleteResponse",
        "ClearResponse",
    ]
    for name in app.models:
        for suffix in expected_suffixes:
            assert f"{name}{suffix}" in schemas


def test_schema_presence_across_app_api_and_tables():
    schemas = spec["components"]["schemas"]
    for name, model in app.models.items():
        assert name in app.models
        assert any(key.startswith(name) for key in schemas)
        assert hasattr(model, "__table__")
        assert len(model.__table__.columns) > 0
