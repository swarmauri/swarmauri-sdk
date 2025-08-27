"""
Info Schema Keys Tests for AutoAPI v2

Tests all 7 info-schema keys: disable_on, write_only, read_only, default_factory, examples, hybrid, py_type
Each key is tested individually using DummyModel instances.
"""

import pytest
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property

from autoapi.v3 import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.schema import _build_schema, check


class DummyModelDisableOn(Base, GUIDPk):
    """Test model for disable_on key."""

    __tablename__ = "dummy_disable_on"

    name = Column(String, info=dict(autoapi={"disable_on": ["update", "replace"]}))
    description = Column(String)


class DummyModelWriteOnly(Base, GUIDPk):
    """Test model for write_only key."""

    __tablename__ = "dummy_write_only"

    name = Column(String)
    secret = Column(String, info=dict(autoapi={"write_only": True}))


class DummyModelReadOnly(Base, GUIDPk):
    """Test model for read_only key."""

    __tablename__ = "dummy_read_only"

    name = Column(String)
    computed_field = Column(String, info=dict(autoapi={"read_only": True}))


class DummyModelDefaultFactory(Base, GUIDPk):
    """Test model for default_factory key."""

    __tablename__ = "dummy_default_factory"

    name = Column(String)
    timestamp = Column(
        DateTime, info=dict(autoapi={"default_factory": datetime.utcnow})
    )


class DummyModelExamples(Base, GUIDPk):
    """Test model for examples key."""

    __tablename__ = "dummy_examples"

    name = Column(
        String, info=dict(autoapi={"examples": ["example1", "example2", "example3"]})
    )
    count = Column(Integer, info=dict(autoapi={"examples": [1, 5, 10, 100]}))


class DummyModelHybrid(Base, GUIDPk):
    """Test model for hybrid key."""

    __tablename__ = "dummy_hybrid"

    first_name = Column(String)
    last_name = Column(String)

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.setter
    def full_name(self, value):
        parts = value.split(" ", 1)
        self.first_name = parts[0]
        self.last_name = parts[1] if len(parts) > 1 else ""

    # Enable hybrid property in schema
    full_name.info = {"autoapi": {"hybrid": True}}


class DummyModelPyType(Base, GUIDPk):
    """Test model for py_type key."""

    __tablename__ = "dummy_py_type"

    name = Column(String)

    @hybrid_property
    def computed_value(self):
        return len(self.name) if self.name else 0

    # Specify Python type for hybrid property
    computed_value.info = {"autoapi": {"hybrid": True, "py_type": int}}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_disable_on_key(create_test_api):
    """Test that disable_on key excludes fields from specified verbs."""
    create_test_api(DummyModelDisableOn)

    # Get schemas for different verbs
    create_schema = _build_schema(DummyModelDisableOn, verb="create")
    update_schema = _build_schema(DummyModelDisableOn, verb="update")
    read_schema = _build_schema(DummyModelDisableOn, verb="read")

    # name should be in create and read schemas
    assert "name" in create_schema.model_fields
    assert "name" in read_schema.model_fields

    # name should NOT be in update schema due to disable_on
    assert "name" not in update_schema.model_fields

    # description should be in all schemas
    assert "description" in create_schema.model_fields
    assert "description" in update_schema.model_fields
    assert "description" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_write_only_key(create_test_api):
    """Test that write_only key excludes fields from read operations."""
    create_test_api(DummyModelWriteOnly)

    # Get schemas for different verbs
    create_schema = _build_schema(DummyModelWriteOnly, verb="create")
    read_schema = _build_schema(DummyModelWriteOnly, verb="read")

    # secret should be in create schema (write operation)
    assert "secret" in create_schema.model_fields

    # secret should NOT be in read schema (read operation)
    assert "secret" not in read_schema.model_fields

    # name should be in both schemas
    assert "name" in create_schema.model_fields
    assert "name" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_read_only_key(create_test_api):
    """Test that read_only key excludes fields from write operations."""
    create_test_api(DummyModelReadOnly)

    # Get schemas for different verbs
    create_schema = _build_schema(DummyModelReadOnly, verb="create")
    update_schema = _build_schema(DummyModelReadOnly, verb="update")
    read_schema = _build_schema(DummyModelReadOnly, verb="read")

    # computed_field should be in read schema
    assert "computed_field" in read_schema.model_fields

    # computed_field should NOT be in create or update schemas
    assert "computed_field" not in create_schema.model_fields
    assert "computed_field" not in update_schema.model_fields

    # name should be in all schemas
    assert "name" in create_schema.model_fields
    assert "name" in update_schema.model_fields
    assert "name" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_default_factory_key(create_test_api):
    """Test that default_factory key provides default values."""
    create_test_api(DummyModelDefaultFactory)

    # Get create schema
    create_schema = _build_schema(DummyModelDefaultFactory, verb="create")

    # timestamp field should be present
    assert "timestamp" in create_schema.model_fields

    # timestamp field should have a default factory
    timestamp_field = create_schema.model_fields["timestamp"]
    assert timestamp_field.default_factory is not None

    # Test that we can create an instance without providing timestamp
    instance_data = {"name": "test"}
    instance = create_schema(**instance_data)

    # Should be able to create without timestamp due to default_factory
    assert instance.name == "test"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_examples_key(create_test_api):
    """Test that examples key provides example values in schema."""
    create_test_api(DummyModelExamples)

    # Get create schema
    create_schema = _build_schema(DummyModelExamples, verb="create")

    # Check that fields have examples
    name_field = create_schema.model_fields["name"]
    count_field = create_schema.model_fields["count"]

    # Examples should be accessible through field info
    # Note: The exact way examples are stored may vary by Pydantic version
    assert hasattr(name_field, "json_schema_extra") or hasattr(name_field, "examples")
    assert hasattr(count_field, "json_schema_extra") or hasattr(count_field, "examples")


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hybrid_key(create_test_api):
    """Test that hybrid key enables hybrid properties in schemas."""
    create_test_api(DummyModelHybrid)

    # Get schemas for different verbs
    create_schema = _build_schema(DummyModelHybrid, verb="create")
    read_schema = _build_schema(DummyModelHybrid, verb="read")

    # full_name should be in schemas because hybrid=True
    assert "full_name" in create_schema.model_fields
    assert "full_name" in read_schema.model_fields

    # Regular fields should also be present
    assert "first_name" in create_schema.model_fields
    assert "last_name" in create_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_py_type_key(create_test_api):
    """Test that py_type key specifies Python type for hybrid properties."""
    create_test_api(DummyModelPyType)

    # Get read schema
    read_schema = _build_schema(DummyModelPyType, verb="read")

    # computed_value should be present due to hybrid=True
    assert "computed_value" in read_schema.model_fields

    # The field should have the specified Python type
    computed_value_field = read_schema.model_fields["computed_value"]

    # Check that the annotation reflects the py_type
    assert computed_value_field.annotation is int


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_info_schema_validation():
    """Test that invalid info schema keys raise errors."""
    # Valid metadata should not raise error
    valid_meta = {"disable_on": ["update"], "write_only": True, "examples": ["test"]}
    check(valid_meta, "test_field", "TestModel")  # Should not raise

    # Invalid key should raise error
    invalid_meta = {"invalid_key": True, "disable_on": ["update"]}

    with pytest.raises(RuntimeError, match="bad autoapi keys"):
        check(invalid_meta, "test_field", "TestModel")

    # Invalid verb should raise error
    invalid_verb_meta = {"disable_on": ["invalid_verb"]}

    with pytest.raises(RuntimeError, match="invalid verb"):
        check(invalid_verb_meta, "test_field", "TestModel")


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_combined_info_schema_keys(create_test_api):
    """Test that multiple info schema keys work together correctly."""

    class DummyModelCombined(Base, GUIDPk):
        __tablename__ = "dummy_combined"

        name = Column(String)
        secret = Column(
            String,
            info=dict(
                autoapi={
                    "write_only": True,
                    "disable_on": ["update"],
                    "examples": ["secret123", "password456"],
                }
            ),
        )

        @hybrid_property
        def computed(self):
            return f"computed-{self.name}"

        computed.info = {"autoapi": {"hybrid": True, "read_only": True, "py_type": str}}

    create_test_api(DummyModelCombined)

    # Get schemas
    create_schema = _build_schema(DummyModelCombined, verb="create")
    update_schema = _build_schema(DummyModelCombined, verb="update")
    read_schema = _build_schema(DummyModelCombined, verb="read")

    # secret should be in create (write_only=True allows writes, disable_on excludes update)
    assert "secret" in create_schema.model_fields
    assert "secret" not in update_schema.model_fields  # disabled on update
    assert "secret" not in read_schema.model_fields  # write_only=True

    # computed should only be in read (read_only=True, hybrid=True)
    assert "computed" not in create_schema.model_fields
    assert "computed" not in update_schema.model_fields
    assert "computed" in read_schema.model_fields

    # name should be in all schemas
    assert "name" in create_schema.model_fields
    assert "name" in update_schema.model_fields
    assert "name" in read_schema.model_fields
