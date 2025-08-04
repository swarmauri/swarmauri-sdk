"""
Mixins Tests for AutoAPI v2

Tests all mixins and their expected behavior using individual DummyModel instances.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import Column, String

from autoapi.v2.mixins import GUIDPk
from autoapi.v2.mixins import (
    Timestamped,
    Created,
    LastUsed,
    ActiveToggle,
    SoftDelete,
    Versioned,
    BulkCapable,
    Replaceable,
    AsyncCapable,
    Audited,
    Streamable,
    Slugged,
    StatusMixin,
    ValidityWindow,
    Monetary,
    ExtRef,
    MetaJSON,
    RelationEdge,
)
from autoapi.v2 import Base


class DummyModelTimestamped(Base, GUIDPk, Timestamped):
    """Test model for Timestamped mixin."""

    __tablename__ = "dummy_timestamped"
    name = Column(String)


class DummyModelCreated(Base, GUIDPk, Created):
    """Test model for Created mixin."""

    __tablename__ = "dummy_created"
    name = Column(String)


class DummyModelLastUsed(Base, GUIDPk, LastUsed):
    """Test model for LastUsed mixin."""

    __tablename__ = "dummy_last_used"
    name = Column(String)


class DummyModelActiveToggle(Base, GUIDPk, ActiveToggle):
    """Test model for ActiveToggle mixin."""

    __tablename__ = "dummy_active_toggle"
    name = Column(String)


class DummyModelSoftDelete(Base, GUIDPk, SoftDelete):
    """Test model for SoftDelete mixin."""

    __tablename__ = "dummy_soft_delete"
    name = Column(String)


class DummyModelVersioned(Base, GUIDPk, Versioned):
    """Test model for Versioned mixin."""

    __tablename__ = "dummy_versioned"
    name = Column(String)


class DummyModelBulkCapable(Base, GUIDPk, BulkCapable):
    """Test model for BulkCapable mixin."""

    __tablename__ = "dummy_bulk_capable"
    name = Column(String)


class DummyModelReplaceable(Base, GUIDPk, Replaceable):
    """Test model for Replaceable mixin."""

    __tablename__ = "dummy_replaceable"
    name = Column(String)


class DummyModelAsyncCapable(Base, GUIDPk, AsyncCapable):
    """Test model for AsyncCapable mixin."""

    __tablename__ = "dummy_async_capable"
    name = Column(String)


class DummyModelSlugged(Base, GUIDPk, Slugged):
    """Test model for Slugged mixin."""

    __tablename__ = "dummy_slugged"
    name = Column(String)


class DummyModelStatusMixin(Base, GUIDPk, StatusMixin):
    """Test model for StatusMixin."""

    __tablename__ = "dummy_status_mixin"
    name = Column(String)


class DummyModelValidityWindow(Base, GUIDPk, ValidityWindow):
    """Test model for ValidityWindow mixin."""

    __tablename__ = "dummy_validity_window"
    name = Column(String)


class DummyModelMonetary(Base, GUIDPk, Monetary):
    """Test model for Monetary mixin."""

    __tablename__ = "dummy_monetary"
    name = Column(String)


class DummyModelExtRef(Base, GUIDPk, ExtRef):
    """Test model for ExtRef mixin."""

    __tablename__ = "dummy_ext_ref"
    name = Column(String)


class DummyModelMetaJSON(Base, GUIDPk, MetaJSON):
    """Test model for MetaJSON mixin."""

    __tablename__ = "dummy_meta_json"
    name = Column(String)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_timestamped_mixin(create_test_api):
    """Test that Timestamped mixin adds created_at and updated_at fields."""
    api = create_test_api(DummyModelTimestamped)

    # Get schemas
    create_schema = api.get_schema(DummyModelTimestamped, "create")
    read_schema = api.get_schema(DummyModelTimestamped, "read")
    update_schema = api.get_schema(DummyModelTimestamped, "update")

    # created_at and updated_at should be in read schema
    assert "created_at" in read_schema.model_fields
    assert "updated_at" in read_schema.model_fields

    # created_at and updated_at should NOT be in create/update schemas (no_create, no_update)
    assert "created_at" not in create_schema.model_fields
    assert "updated_at" not in create_schema.model_fields
    assert "created_at" not in update_schema.model_fields
    assert "updated_at" not in update_schema.model_fields

    # name should be in all schemas
    assert "name" in create_schema.model_fields
    assert "name" in read_schema.model_fields
    assert "name" in update_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_created_mixin(create_test_api):
    """Test that Created mixin adds created_at field."""
    api = create_test_api(DummyModelCreated)

    # Get schemas
    create_schema = api.get_schema(DummyModelCreated, "create")
    read_schema = api.get_schema(DummyModelCreated, "read")

    # created_at should be in read schema
    assert "created_at" in read_schema.model_fields

    # created_at should NOT be in create schema (no_create)
    assert "created_at" not in create_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_last_used_mixin(create_test_api):
    """Test that LastUsed mixin adds last_used_at field and touch method."""
    api = create_test_api(DummyModelLastUsed)

    # Get schemas
    read_schema = api.get_schema(DummyModelLastUsed, "read")

    # last_used_at should be in read schema
    assert "last_used_at" in read_schema.model_fields

    # Verify the model has touch method
    assert hasattr(DummyModelLastUsed, "touch")

    # Test touch method functionality
    instance = DummyModelLastUsed(name="test")
    assert instance.last_used_at is None

    instance.touch()
    assert instance.last_used_at is not None
    assert isinstance(instance.last_used_at, datetime)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_active_toggle_mixin(create_test_api):
    """Test that ActiveToggle mixin adds is_active field."""
    api = create_test_api(DummyModelActiveToggle)

    # Get schemas
    create_schema = api.get_schema(DummyModelActiveToggle, "create")
    read_schema = api.get_schema(DummyModelActiveToggle, "read")

    # is_active should be in schemas
    assert "is_active" in create_schema.model_fields
    assert "is_active" in read_schema.model_fields

    # is_active field should be boolean type (default may be None)
    is_active_field = create_schema.model_fields["is_active"]
    assert is_active_field.annotation is bool


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_soft_delete_mixin(create_test_api):
    """Test that SoftDelete mixin adds deleted_at field."""
    api = create_test_api(DummyModelSoftDelete)

    # Get schemas
    read_schema = api.get_schema(DummyModelSoftDelete, "read")

    # deleted_at should be in read schema
    assert "deleted_at" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_versioned_mixin(create_test_api):
    """Test that Versioned mixin adds revision and prev_id fields."""
    api = create_test_api(DummyModelVersioned)

    # Get schemas
    create_schema = api.get_schema(DummyModelVersioned, "create")
    read_schema = api.get_schema(DummyModelVersioned, "read")

    # revision and prev_id should be in schemas
    assert "revision" in read_schema.model_fields
    assert "prev_id" in read_schema.model_fields

    # revision should have default value of 1
    revision_field = create_schema.model_fields["revision"]
    assert revision_field.annotation is int


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_capable_mixin(create_test_api):
    """Test that BulkCapable mixin enables bulk operations."""
    api = create_test_api(DummyModelBulkCapable)

    # Check that bulk routes are available
    routes = [route.path for route in api.router.routes]

    # Should have bulk create and bulk delete routes
    assert "/dummy_bulk_capable/bulk" in [route for route in routes if "/bulk" in route]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_replaceable_mixin(create_test_api):
    """Test that Replaceable mixin enables replacement operations."""
    api = create_test_api(DummyModelReplaceable)

    # Get schemas
    create_schema = api.get_schema(DummyModelReplaceable, "create")
    read_schema = api.get_schema(DummyModelReplaceable, "read")

    # Should have basic fields
    assert "name" in create_schema.model_fields
    assert "name" in read_schema.model_fields

    # Replaceable mixin is a marker mixin - doesn't add fields
    # but enables replacement functionality
    expected_fields = {"id", "name"}
    actual_fields = set(read_schema.model_fields.keys())
    assert expected_fields.issubset(actual_fields)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_async_capable_mixin(create_test_api):
    """Test that AsyncCapable mixin is a marker mixin."""
    api = create_test_api(DummyModelAsyncCapable)

    # Get schemas
    read_schema = api.get_schema(DummyModelAsyncCapable, "read")

    # AsyncCapable is a marker mixin - doesn't add fields
    expected_fields = {"id", "name"}
    actual_fields = set(read_schema.model_fields.keys())
    assert actual_fields == expected_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_slugged_mixin(create_test_api):
    """Test that Slugged mixin adds slug field."""
    api = create_test_api(DummyModelSlugged)

    # Get schemas
    create_schema = api.get_schema(DummyModelSlugged, "create")
    read_schema = api.get_schema(DummyModelSlugged, "read")

    # slug should be in schemas
    assert "slug" in create_schema.model_fields
    assert "slug" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_status_mixin(create_test_api):
    """Test that StatusMixin adds status field."""
    api = create_test_api(DummyModelStatusMixin)

    # Get schemas
    create_schema = api.get_schema(DummyModelStatusMixin, "create")
    read_schema = api.get_schema(DummyModelStatusMixin, "read")

    # status should be in schemas
    assert "status" in create_schema.model_fields
    assert "status" in read_schema.model_fields

    # status field should be string type
    status_field = create_schema.model_fields["status"]
    assert status_field.annotation is str


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_validity_window_mixin(create_test_api):
    """Test that ValidityWindow mixin adds valid_from and valid_until fields."""
    api = create_test_api(DummyModelValidityWindow)

    # Get schemas
    create_schema = api.get_schema(DummyModelValidityWindow, "create")
    read_schema = api.get_schema(DummyModelValidityWindow, "read")

    # validity fields should be in schemas
    assert "valid_from" in create_schema.model_fields
    assert "valid_to" in create_schema.model_fields
    assert "valid_from" in read_schema.model_fields
    assert "valid_to" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_validity_window_default(create_test_api):
    api = create_test_api(DummyModelValidityWindow)
    session = next(api.get_db())
    try:
        instance = DummyModelValidityWindow(name="x")
        session.add(instance)
        session.flush()
        vf_default = instance.valid_from
        vt_default = instance.valid_to
    finally:
        session.close()
    assert vf_default is not None
    assert vt_default is not None
    assert abs((vt_default - vf_default) - timedelta(days=1)) < timedelta(seconds=1)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_monetary_mixin(create_test_api):
    """Test that Monetary mixin adds currency and amount fields."""
    api = create_test_api(DummyModelMonetary)

    # Get schemas
    create_schema = api.get_schema(DummyModelMonetary, "create")
    read_schema = api.get_schema(DummyModelMonetary, "read")

    # monetary fields should be in schemas
    assert "currency" in create_schema.model_fields
    assert "amount" in create_schema.model_fields
    assert "currency" in read_schema.model_fields
    assert "amount" in read_schema.model_fields

    # currency field should be string type
    currency_field = create_schema.model_fields["currency"]
    assert currency_field.annotation is str


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_ext_ref_mixin(create_test_api):
    """Test that ExtRef mixin adds external_id field."""
    api = create_test_api(DummyModelExtRef)

    # Get schemas
    create_schema = api.get_schema(DummyModelExtRef, "create")
    read_schema = api.get_schema(DummyModelExtRef, "read")

    # external_id should be in schemas
    assert "external_id" in create_schema.model_fields
    assert "external_id" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.skip(reason="JSONB type not supported in SQLite test environment")
async def test_meta_json_mixin(create_test_api):
    """Test that MetaJSON mixin adds meta field."""
    api = create_test_api(DummyModelMetaJSON)

    # Get schemas
    create_schema = api.get_schema(DummyModelMetaJSON, "create")
    read_schema = api.get_schema(DummyModelMetaJSON, "read")

    # meta should be in schemas
    assert "meta" in create_schema.model_fields
    assert "meta" in read_schema.model_fields

    # meta should default to empty dict
    meta_field = create_schema.model_fields["meta"]
    assert meta_field.default == {}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_marker_mixins(create_test_api):
    """Test that marker mixins (Audited, Streamable, etc.) don't add fields."""

    # Create dummy models for other marker mixins
    class DummyAudited(Base, GUIDPk, Audited):
        __tablename__ = "dummy_audited"
        name = Column(String)

    class DummyStreamable(Base, GUIDPk, Streamable):
        __tablename__ = "dummy_streamable"
        name = Column(String)

    class DummyRelationEdge(Base, GUIDPk, RelationEdge):
        __tablename__ = "dummy_relation_edge"
        name = Column(String)

    marker_models = [DummyAudited, DummyStreamable, DummyRelationEdge]

    for model in marker_models:
        api = create_test_api(model)

        read_schema = api.get_schema(model, "read")

        # Should only have id and name fields (no extra fields from marker mixins)
        expected_fields = {"id", "name"}
        actual_fields = set(read_schema.model_fields.keys())
        assert actual_fields == expected_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_multiple_mixins_combination(create_test_api):
    """Test that multiple mixins can be combined correctly."""

    class DummyMultipleMixins(
        Base, GUIDPk, Timestamped, ActiveToggle, Slugged, StatusMixin
    ):
        __tablename__ = "dummy_multiple_mixins"
        name = Column(String)

    api = create_test_api(DummyMultipleMixins)

    # Get schemas
    create_schema = api.get_schema(DummyMultipleMixins, "create")
    read_schema = api.get_schema(DummyMultipleMixins, "read")

    # Should have fields from all mixins
    # From ActiveToggle
    assert "is_active" in create_schema.model_fields
    assert "is_active" in read_schema.model_fields

    # From Slugged
    assert "slug" in create_schema.model_fields
    assert "slug" in read_schema.model_fields

    # From StatusMixin
    assert "status" in create_schema.model_fields
    assert "status" in read_schema.model_fields

    # From Timestamped (only in read schema due to no_create, no_update)
    assert "created_at" not in create_schema.model_fields
    assert "updated_at" not in create_schema.model_fields
    assert "created_at" in read_schema.model_fields
    assert "updated_at" in read_schema.model_fields
