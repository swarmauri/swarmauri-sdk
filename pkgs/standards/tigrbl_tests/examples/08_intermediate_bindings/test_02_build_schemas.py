"""Lesson 08.2: Building request/response schemas."""

from tigrbl import Base, bind, build_schemas
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_build_schemas_returns_schema_map():
    """Explain that schema builders attach named schema namespaces.

    Purpose: confirm that schema creation materializes a `schemas` namespace
    on the model so consumers can introspect request/response shapes.
    Design practice: use generated schemas to keep docs and validation aligned.
    """

    # Setup: declare a model with a single field.
    class LessonSchemas(Base, GUIDPk):
        __tablename__ = "lesson_schemas"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind the model to generate OpSpecs.
    specs = bind(LessonSchemas)

    # Test: build schemas for the bound model.
    build_schemas(LessonSchemas, specs)

    # Assertion: the model now exposes a schemas namespace.
    assert hasattr(LessonSchemas, "schemas")


def test_build_schemas_creates_per_op_namespace():
    """Show that each op gets its own schema namespace.

    Purpose: verify that canonical operations (like list) create a namespaced
    schema entry for consistent access patterns.
    Design practice: favor per-op schema namespaces for clarity in integrations.
    """

    # Setup: define a model for schema generation.
    class LessonSchemasNamespace(Base, GUIDPk):
        __tablename__ = "lesson_schemas_namespace"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind and then build schemas.
    specs = bind(LessonSchemasNamespace)
    build_schemas(LessonSchemasNamespace, specs)

    # Test: check that per-op schema namespaces exist.
    assert hasattr(LessonSchemasNamespace.schemas, "list")
